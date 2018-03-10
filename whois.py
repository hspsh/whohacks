#!/usr/bin/python3
from urllib.parse import urlparse, urljoin
from flask import Flask, flash, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import sqlite3
import json
import re

import settings


class Device():
    """docstring for Device"""
    def __init__(self, mac_addr, last_seen, user_id=None):
        self.mac_addr = mac_addr
        self.last_seen = last_seen
        self.user_id = user_id
        self.user_display = None
        self.tags = []


    def get_device(cursor, mac_addr):
        """Get device info"""
        cursor.execute('SELECT mac_addr, last_seen, user_id FROM whois_devices WHERE mac_addr=?', (mac_addr, ))
        device = cursor.fetchone()
        assert device[0] == mac_addr
        return Device(*device)


    def is_tagged(self, tag):
        return False


    def get_tags(self):
        if self.is_tagged('invisible') is False or current_user.get_id() == self.user_id:
            return self.tags


class User():
    """docstring for User"""
    def __init__(self, id, login, display_name):
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

        self.id = id
        self.login = login
        self.display_name = display_name


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


    def get_devices(self, cursor):
        cursor.execute('SELECT mac_addr, last_seen, user_id FROM whois_devices WHERE user_id=?', (self.id, ))
        return cursor.fetchall()

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

    def is_tagged(self, tag):
        return False



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


def post_device_claim(cursor, mac_addr, new_user_id):
    """Attach user id to given mac address"""
    assert len(mac_addr) == 17
    cursor.execute('SELECT user_id FROM whois_devices WHERE mac_addr=?', (mac_addr, ))
    user_id = cursor.fetchone()[0]
    if user_id == None or user_id == current_user.get_id():
        cursor.execute('''UPDATE whois_devices SET user_id=? WHERE mac_addr=?''', (new_user_id, mac_addr))
    

# def post_device_tags(cursor, mac_addr, user_id):
#     """Attach user id to given mac address"""
#     assert len(mac_addr) == 17
#     cursor.execute('SELECT user_id FROM whois_devices WHERE mac_addr=?', (mac_addr, ))
#     user_id = cursor.fetchone()
#     if user_id == None or user_id == current_user.get_id():
#         cursor.execute('''UPDATE whois_devices SET user_id=? WHERE mac_addr=?''', (user_id, mac_addr))


def get_device(cursor, mac_addr):
    """Get device info"""
    dev = Device.get_device(cursor, mac_addr)
    return {'mac_addr':dev.mac_addr, 
        'last_seen':dev.last_seen, 
        'claim':dev.user_id, 
        'tags':[]}

def get_recent_devices(cursor, hours=0, minutes=30, seconds=0):
    """Get recent devices, from last 30 min by default"""
    min_dt = datetime.now() - timedelta(hours=hours, minutes=minutes, seconds=seconds)

    cursor = db.cursor()
    cursor.execute("SELECT * FROM whois_devices WHERE last_seen BETWEEN ? AND DATETIME('NOW')", (min_dt, ))

    return [row for row in cursor]


def get_users_at_space(cursor, devices):
    """Get users at space based on given devices, filter by tags"""
    users = {}
    for device in devices:
        cursor.execute('SELECT user_id, display_name FROM whois_users WHERE user_id=?', (device['user_id'], ))



@login_manager.user_loader
def load_user(user_id):
    cursor = db.cursor()
    user = User.get_by_id(cursor, user_id)
    return user


@app.route('/')
def index():
    """Serve list of people in hs, listen for data but only from whitelisted devices"""
    unclaimed = None
    mine = None
    if current_user.is_authenticated:
        cursor = db.cursor()
        recent = get_recent_devices(cursor, 12)
        unclaimed = [dev for dev in recent if dev[2] is None]
        mine = current_user.get_devices(cursor)
    return render_template('index.html', devices={'unclaimed':unclaimed, 'mine':mine})


@app.route('/now', methods=['GET'])
def now_at_space():
    """Send list of people currently in HS as JSON, only registred people, used by other services in HS,
    requests should be from hs3.pl domain or from HSWAN"""
    cursor = db.cursor()
    devices = get_recent_devices(cursor, 10)
    user_ids = set([device[2] for device in devices if device[2] is not None])
    users = [User.get_by_id(cursor, id) for id in user_ids]
    # should I commit?

    return jsonify({"users": sorted(map(lambda u: u.display_name, users)),
        "unknown": len([dev for dev in devices if dev[2] is None])})


@app.route('/lastseen', methods=['POST'])
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
# @login_required
def device(mac_addr):
    """Get info about device, claim device, release device"""
    cursor = db.cursor()

    if request.method == 'POST':
        print(request.values.get('action'))
        if request.values.get('action') == 'claim':
            post_device_claim(cursor, mac_addr, current_user.get_id())
            flash('Claimed {}!'.format(mac_addr), 'alert-success')
        if request.values.get('action') == 'unclaim':
            post_device_claim(cursor, mac_addr, None)
            flash('Unclaimed {}!'.format(mac_addr), 'alert-info')

        if request.values.get('tags'):
            flash('Can\'t set tags to {}! Unimplemented'.format(mac_addr), 'alert-danger')

    db.commit()
    device = get_device(cursor, mac_addr)
    return render_template('device.html', device=device)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration form"""
    if request.method == 'POST':
        display_name = request.form['display_name']
        login = request.form['username']
        password = generate_password_hash(request.form['password'])

        print(request.form)

        cursor = db.cursor()
        cursor.execute("INSERT INTO whois_users (login, display_name, password, registered_at, last_login) VALUES (?,?,?,DATETIME('NOW'),DATETIME('NOW'))", (login, display_name, password))
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
    c.execute('CREATE TABLE IF NOT EXISTS whois_history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date_from DATETIME, date_to DATETIME)')
 
    db.commit()

    app.run()
