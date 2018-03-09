#!/usr/bin/python3
from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required
from datetime import datetime, timedelta
import sqlite3
import json
import re

from pprint import pprint


app = Flask(__name__)
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


def last_seen_to_timestamp(dt_now, duration):
    last_seen = dt_now - parse_duration(duration)
    return last_seen.timestamp()


def parse_mikrotik_data(data):
    assert type(data) is list

    dt_now = datetime.now()
    extracted = [(device['mac'].upper(), int(last_seen_to_timestamp(dt_now, device['last']))) for device in data]
    return extracted


def post_last_seen_devices(db, devices):
    """POST last seen devices to db, update last seen date if exists"""

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    """Serve list of people in hs, listen for data but only from whitelisted devices"""
    return render_template('index.html')

@app.route('/now', methods=['GET'])
def now_at_space():
    """Send list of people currently in HS as JSON, only registred people, used by other services in HS,
    requests should be from hs3.pl domain or from HSWAN
    Listen for data from whitelisted devices"""
    pass

@app.route('/lastseen', methods=['POST'])
def last_seen_devices():
    """Post devices lastseen by mikrotik to database database"""
    data = request.get_json()

    parsed_data = parse_mikrotik_data(data)
    

@app.route('/device/<mac>', methods=['GET', 'POST']) # NOTE: Nie jestem pewny czy dawać każdemu urządzeniu id czy mac. w bazie danych mogą mieć id itp, ale requesty mogą się odbywać na podstawie maców, i może łatwiej wykryć kolizje. nie wiem
@login_required
def device():
    """Get info about device, claim device, release device"""
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login using naive db or LDAP (work on it @priest)"""
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    pass


if __name__ == '__main__':

    db = sqlite3.connect('whosdevices.db')

    c = db.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS whois_users (id INTEGER PRIMARY KEY AUTOINCREMENT, display_name VARCHAR(100), login VARCHAR(32) UNIQUE, password VARCHAR(64), access_key VARCHAR(10), registered_at INTEGER, last_login INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS whois_devices (mac_addr VARCHAR(17) PRIMARY KEY UNIQUE, user_id INTEGER, last_seen INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS whois_history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date_from INTEGER, date_to INTEGER)')
 
    db.commit()

    app.run()
