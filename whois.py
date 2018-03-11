#!/usr/bin/python3
from urllib.parse import urlparse, urljoin
from flask import Flask, flash, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import sqlite3
import json
import re

import settings


class Device():
    """docstring for Device"""
    def __init__(self, mac_addr, last_seen, user_id=None):
        assert len(mac_addr) == 17
        self.mac_addr = mac_addr
        self.host_name = None
        self.last_seen = last_seen
        self.user_id = user_id
        self.user_display = None


    def __str__(self):
        return '[{}]'.format(self.mac_addr)


    @staticmethod
    def get_by_mac(cursor, mac_addr):
        """Get device info"""
        cursor.execute('SELECT mac_addr, last_seen, user_id FROM whois_devices WHERE mac_addr=?', (mac_addr, ))
        try:
            return Device(*cursor.fetchone())
        except TypeError:
            return None

    @staticmethod
    def get_recent(cursor, hours=0, minutes=30, seconds=0):
        """Get recent devices, from last 30 min by default"""
        min_dt = datetime.now() - timedelta(hours=hours, minutes=minutes, seconds=seconds)

        cursor.execute("SELECT mac_addr, last_seen, user_id FROM whois_devices WHERE last_seen BETWEEN ? AND DATETIME('NOW')", (min_dt, ))

        return [Device(*row) for row in cursor]


    def claim(self, cursor, new_user_id):
        """Attach user id to given mac address"""
        if self.user_id == None or self.user_id == current_user.get_id():
            self.user_id = new_user_id
            cursor.execute('UPDATE whois_devices SET user_id=? WHERE mac_addr=?', 
                (self.user_id, self.mac_addr))

    def unclaim(self, cursor):
        """Attach user id to given mac address"""
        if self.user_id == current_user.get_id():
            self.user_id = new_user_id
            cursor.execute('UPDATE whois_devices SET user_id=NULL WHERE mac_addr=?', 
                (self.mac_addr,))

    @property
    def owner(self):
        return self.user_id

    def is_tagged(self, tag):
        pass


    def get_tags(self):
        pass


class User(UserMixin):
    """docstring for User"""
    def __init__(self, id, login, display_name):
        self.id = id
        self.login = login
        self.display_name = display_name
        self.tags = []

    def __str__(self):
        if 'hidden' in self.tags:
            return None
        elif 'anonymous' in self.tags:
            return 'Anonymous'
        elif self.display_name is not None:
            return self.display_name
        else:
            return self.login


    @staticmethod
    def get_by_id(cursor, user_id):
        cursor.execute('SELECT id, login, display_name FROM whois_users WHERE id=?', (user_id, ))
        try:
            return User(*cursor.fetchone())
        except TypeError:
            return None

    @staticmethod
    def get_by_login(cursor, login):
        cursor.execute('SELECT id, login, display_name FROM whois_users WHERE login=?', (login, ))
        try:
            return User(*cursor.fetchone())
        except TypeError:
            return None


    @staticmethod
    def register(cursor, login, display_name, password):
        cursor.execute("INSERT INTO whois_users (login, display_name, password, registered_at, last_login) VALUES (?,?,?,DATETIME('NOW'),DATETIME('NOW'))", (login, display_name, password))


    def auth(self, cursor, pwd):
        cursor.execute('SELECT password FROM whois_users WHERE login=?', (self.login, ))
        hash = cursor.fetchone()[0]
        if check_password_hash(hash, pwd):
            return True
        else:
            return False


    def set_password(self, cursor, pwd):
        cursor.execute('UPDATE whois_users SET password=? WHERE id=?', (generate_password_hash(pwd), self.id))

        
    def get_id(self):
        return str(self.id)


    def get_claimed_devices(self, cursor):
        cursor.execute('SELECT mac_addr, last_seen, user_id FROM whois_devices WHERE user_id=?', (self.id, ))
        return [Device(*row) for row in cursor.fetchall()]


    def is_tagged(self, tag):
        pass



app = Flask(__name__)
app.secret_key = settings.secret_key
login_manager = LoginManager()
login_manager.init_app(app)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


duration_re = re.compile(r'((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

def parse_duration(duration_str):
    parts = duration_re.match(duration_str)
    if not parts:
        return
    parts = parts.groupdict()
    print (parts)
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)

    time_params['days'] = time_params.get('days', 0) + 7 * time_params.get('weeks', 0)
    time_params.pop('weeks', None)

    return timedelta(**time_params)


def parse_mikrotik_data(data):
    """Returns list of mac adress, last seen datetime
    >>> parse_mikrtotik_data([{"mac":"11:22:33:44:55:66","name":"Dom","last":"50w6d16h1m10s","status":"waiting"},{"mac":"AA:BB:CC:DD:EE:FF","name":"HS","last":"4d1h58m8s","status":"bound"}])
     [('11:22:33:44:55:66', '2018-02-20 21:37'), ('AA:BB:CC:DD:EE:FF', '2018-02-20 21:37')]"""
    assert type(data) is list

    dt_now = datetime.now()
    extracted = [(device['mac'].upper(),
        dt_now - parse_duration(device['last'])) for device in data]
    return extracted


def post_last_seen_devices(cursor, devices):
    """POST last seen devices to db, update last seen date if exists"""
    for device in devices:
        assert type(device[0]) is str
        assert len(device[0]) == 17
        assert type(device[1]) is datetime

    
    cursor.executemany('''INSERT INTO whois_devices (mac_addr, last_seen) VALUES (?,?) 
        ON DUPLICATE KEY UPDATE
        last_seen = VALUES(last_seen)''', devices)


def get_users_at_space(cursor, devices):
    """Get users at space based on given devices, filter by tags"""
    users = {}
    for device in devices:
        cursor.execute('SELECT user_id, display_name FROM whois_users WHERE user_id=?', (device['user_id'], ))



@login_manager.user_loader
def load_user(user_id):
    cursor = db.cursor()
    return User.get_by_id(cursor, user_id)
    


@app.route('/')
def index():
    """Serve list of people in hs, listen for data but only from whitelisted devices"""
    unclaimed = None
    mine = None
    if current_user.is_authenticated:
        cursor = db.cursor()
        recent = Device.get_recent(cursor, 12)
        unclaimed = [dev for dev in recent if dev.owner is None]
        mine = current_user.get_claimed_devices(cursor)
    return render_template('index.html', devices={'unclaimed':unclaimed, 'mine':mine})


@app.route('/api/now', methods=['GET'])
def now_at_space():
    """Send list of people currently in HS as JSON, only registred people, used by other services in HS,
    requests should be from hs3.pl domain or from HSWAN"""
    cursor = db.cursor()
    devices = get_recent_devices(cursor, 10)
    user_ids = set([device.owner for device in devices if device.owner is not None])
    users = [User.get_by_id(cursor, id) for id in user_ids]
    # should I commit?

    return jsonify({"users": sorted(map(str, users)),
        "unknown": len([dev for dev in devices if dev.owner is None])})


@app.route('/api/lastseen', methods=['POST'])
def last_seen_devices():
    """Post devices last seen by mikrotik to database
    Listen only for whitelisted devices"""
    if request.remote_addr in settings.whitelist:
        data = request.get_json()
        parsed_data = parse_mikrotik_data(data)

        cursor = db.cursor()
        post_last_seen_devices(cursor, parsed_data)
        db.commit()


@app.route('/device/<mac_addr>', methods=['GET', 'POST']) # NOTE: Nie jestem pewny czy dawać każdemu urządzeniu id czy mac. w bazie danych mogą mieć id itp, ale requesty mogą się odbywać na podstawie maców, i może łatwiej wykryć kolizje. nie wiem
@login_required
def device(mac_addr):
    """Get info about device, claim device, release device"""
    cursor = db.cursor()
    device = Device.get_by_mac(cursor, mac_addr)
    if request.method == 'POST':
        print(request.values.get('action'))
        if request.values.get('action') == 'claim':
            device.claim(cursor, current_user.get_id())
            flash('Claimed {}!'.format(mac_addr), 'alert-success')

        elif request.values.get('action') == 'unclaim':
            device.unclaim(cursor)
            flash('Unclaimed {}!'.format(mac_addr), 'alert-info')

        if request.values.get('tags'):
            flash('Can\'t set tags to {}! Unimplemented'.format(mac_addr), 'alert-danger')

    db.commit()
    return render_template('device.html', device={'mac_addr':device.mac_addr, 
        'last_seen':device.last_seen, 
        'claim':str(User.get_by_id(cursor, device.user_id))})


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration form"""
    if request.method == 'POST':
        #TODO: WTF forms or safer method
        display_name = request.form['display_name']
        login = request.form['username']
        password = generate_password_hash(request.form['password'])

        cursor = db.cursor()
        User.register(cursor, login, display_name, password)
        db.commit()
        flash('Registred.', 'alert-info')

        return redirect(url_for('login'))

    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login using naive db or LDAP (work on it @priest)"""
    if request.method == 'POST':
        cursor = db.cursor()
        user = User.get_by_login(cursor, request.form['username'])
        if user is not None and user.auth(cursor, request.form['password']) == True:
            login_user(user) 
            flash('Hello {}! You can now claim and manage your devices.'.format(current_user.login), 'alert-success')
            return redirect(url_for('index'))
        else:
            flash('Indvalid creditentials', 'alert-danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'alert-info')
    return redirect(url_for('index'))


if __name__ == '__main__':

    db = sqlite3.connect('whosdevices.db')

    c = db.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS whois_users (id INTEGER PRIMARY KEY AUTOINCREMENT, display_name VARCHAR(100), login VARCHAR(32) UNIQUE, password VARCHAR(64), registered_at DATETIME, last_login DATETIME)')
    c.execute('CREATE TABLE IF NOT EXISTS whois_devices (mac_addr VARCHAR(17) PRIMARY KEY UNIQUE, last_seen DATETIME, user_id INTEGER, tags VARCHAR(32))')
 
    db.commit()

    app.run()
