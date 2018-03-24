#!/usr/bin/python3
import json
from datetime import datetime

from flask import Flask, flash, render_template, redirect, url_for, request, \
    jsonify, abort
from flask_login import LoginManager, login_required, current_user, login_user, \
    logout_user

from whois import settings
from whois.database import db, Device, User
from whois.utility import parse_mikrotik_data

app = Flask(__name__)
app.secret_key = settings.secret_key
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = User.get_by_id(user_id)

    #TODO: do modelu
    user.is_authenticated = True
    user.is_anonymous = False

    return user


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route('/')
def index():
    """Serve list of people in hs, show panel for logged users"""
    unclaimed = None
    mine = None
    recent = Device.get_recent(12)
    users = set(
        [device.owner for device in recent if device.owner is not None])
    if current_user.is_authenticated:
        unclaimed = [dev for dev in recent if dev.owner is None]
        mine = [device for device in current_user.devices]

    return render_template('index.html',
                           devices={'unclaimed': unclaimed, 'mine': mine},
                           users=users)


@app.route('/api/now', methods=['GET'])
def now_at_space():
    """
    Send list of people currently in HS as JSON, only registred people,
    used by other services in HS,
    requests should be from hs3.pl domain or from HSWAN
    """
    devices = Device.get_recent()
    users = [device.owner.display_name for device in devices if
             device.owner is not None]
    users = set(users)
    return jsonify({"users": sorted(users),
                    "user_count": len(users),
                    "unknown_devices": len(
                        [dev for dev in devices if dev.owner is None])})


@app.route('/api/last_seen', methods=['POST'])
def last_seen_devices():
    """
    Post last seen devices to database
    :return: 200
    """
    if True or request.remote_addr in settings.whitelist:
        if request.is_json:
            data = request.get_json()
        elif request.headers.get('User-Agent') == 'Mikrotik/6.x Fetch':
            data = json.loads(request.values.get('data', []))
        else:
            data = []
            abort(501)

        parsed_data = parse_mikrotik_data(datetime.now(), data)

        with db.atomic():
            for dev in parsed_data:
                Device.update_or_create(**dev)

        return 'OK', 200


@app.route('/device/<mac_address>', methods=['GET', 'POST'])
@login_required
def device(mac_address):
    """Get info about device, claim device, release device"""
    device = Device.get(Device.mac_address == mac_address)
    if request.method == 'POST':
        print('Got action: ' + request.values.get('action'))
        if request.values.get('action') == 'claim' and device.owner is None:
            device.owner = current_user.get_id()
            flash('Claimed {}!'.format(mac_address), 'alert-success')
            device.save()
            # return 'OK', 200
        elif request.values.get(
                'action') == 'unclaim' and device.owner.get_id() == current_user.get_id():
            device.owner = None
            device.save()
            flash('Unclaimed {}!'.format(mac_address), 'alert-info')
            # return 'OK', 200

        if request.values.get('tags'):
            flash('Can\'t set tags to {}! Unimplemented'.format(mac_address),
                  'alert-danger')
            # return 'Not implemented', 501

    if device.owner is not None:
        owner = device.owner.username
    else:
        owner = None

    return render_template('device.html',
                           device={'mac_address': device.mac_address,
                                   'last_seen': device.last_seen,
                                   'owner': owner})


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration form"""
    if request.method == 'POST':
        # TODO: WTF forms dla lepszego bezpieczeństwa
        display_name = request.form['display_name']
        username = request.form['username']
        password = request.form['password']

        user = User.register(username, password, display_name)
        user.save()

        flash('Registered.', 'alert-info')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login using naive db or LDAP (work on it @priest)"""
    if request.method == 'POST':
        user = User.get(User.username == request.form['username'])
        if user is not None and user.auth(request.form['password']) is True:
            login_user(user)
            flash(
                'Hello {}! You can now claim and manage your devices.'.format(
                    current_user.username), 'alert-success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'alert-danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'alert-info')
    return redirect(url_for('index'))
