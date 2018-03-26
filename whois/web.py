#!/usr/bin/python3
import json
import logging
from datetime import datetime

from flask import Flask, flash, render_template, redirect, url_for, request, \
    jsonify, abort
from flask_login import LoginManager, login_required, current_user, login_user, \
    logout_user

from whois import settings
from whois.database import db, Device, User
from whois.mikrotik import parse_mikrotik_data
from whois.helpers import owners_from_devices, filter_hidden, unclaimed_devices, filter_usernames, count

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.secret_key = settings.secret_key
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.before_request
def before_request():
    logging.info('connecting to db')
    db.connect()


@app.teardown_appcontext
def after_request(error):
    logging.info('closing db')
    db.close()
    if error:
        logger.error(error)


@app.route('/')
def index():
    """Serve list of people in hs, show panel for logged users"""
    unclaimed = None
    mine = None
    recent = Device.get_recent(**settings.recent_time)
    users = filter_hidden(owners_from_devices(recent))

    if current_user.is_authenticated:
        unclaimed = unclaimed_devices(recent)
        mine = current_user.devices

    return render_template('index.html',
                           devices={'unclaimed': unclaimed, 'mine': mine},
                           users=filter_usernames(users), headcount=count(users))


@app.route('/api/now', methods=['GET'])
def now_at_space():
    """
    Send list of people currently in HS as JSON, only registred people,
    used by other services in HS,
    requests should be from hs3.pl domain or from HSWAN
    """
    devices = filter_hidden(Device.get_recent(**settings.recent_time))
    users = filter_hidden(owners_from_devices(devices))

    data = {"users": sorted(map(str, filter_usernames(users))),
            "headcount": count(users),
            "unknown_devices": count(unclaimed_devices(devices))}

    logger.info('sending request for /api/now {}'.format(data))

    return jsonify(data)


@app.route('/api/last_seen', methods=['POST'])
def last_seen_devices():
    """
    Post last seen devices to database
    :return: status code
    """
    if request.remote_addr in settings.whitelist:
        logger.info(
            'request from whitelist: {}'.format(request.remote_addr))
        if request.is_json:
            logger.info('got json')
            data = request.get_json()
        elif request.headers.get('User-Agent') == 'Mikrotik/6.x Fetch':
            logger.info('got data from mikrotik')
            data = json.loads(request.values.get('data', []))
        else:
            data = []
            logger.warning('bad request \n{}'.format(request.headers))
            abort(400)

        parsed_data = parse_mikrotik_data(datetime.now(), data)
        logger.info('parsed data, got {} devices'.format(len(parsed_data)))

        with db.atomic():
            for dev in parsed_data:
                Device.update_or_create(**dev)

        logger.info('updated last seen devices')

        return 'OK', 200
    else:
        logger.warning(
            'request from outside whitelist: {}'.format(request.remote_addr))
        return 'NOPE', 403


@app.route('/device/<mac_address>', methods=['GET', 'POST'])
@login_required
def device(mac_address):
    """Get info about device, claim device, release device"""
    device = Device.get(Device.mac_address == mac_address)
    if request.method == 'POST':
        if request.values.get('action') == 'claim' and device.owner is None:
            device.owner = current_user.get_id()
            device.save()
            logger.info(
                '{} claim {}'.format(current_user.username, mac_address))
            flash('Claimed {}!'.format(mac_address), 'alert-success')

        elif request.values.get(
                'action') == 'unclaim' and device.owner.get_id() == current_user.get_id():
            device.owner = None
            device.save()
            logger.info(
                '{} unclaim {}'.format(current_user.username, mac_address))
            flash('Unclaimed {}!'.format(mac_address), 'alert-info')
        if request.values.get('flags'):
            new_flags = request.form.getlist('flags')

            device.is_hidden = 'hidden' in new_flags
            device.is_esp = 'esp' in new_flags
            device.is_infrastructure = 'infrastructure' in new_flags
            print(device.flags)
            device.save()

            logger.info(
                '{} changed {} flags to {}'.format(current_user.username,
                                                   mac_address, device.flags))
            flash('Flags set'.format(mac_address), 'alert-info')

    return render_template('device.html', device=device)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration form"""
    if request.method == 'POST':
        # TODO: WTF forms dla lepszego bezpieczeństwa
        display_name = request.form['display_name']
        username = request.form['username']
        password = request.form['password']

        try:
            user = User.register(username, password, display_name)
        except Exception as exc:
            if exc.args[0] == 'too_short':
                flash('Password too short, minimum length is 3')
            else:
                print(exc)
        else:
            user.save()
            logger.info('registred new user: {}'.format(user.username))
            flash('Registered.', 'alert-info')

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login using naive db or LDAP (work on it @priest)"""
    if request.method == 'POST':
        try:
            user = User.get(User.username == request.form['username'])
        except User.DoesNotExist:
            user = None

        if user is not None and user.auth(request.form['password']) is True:
            login_user(user)
            logger.info('logged in: {}'.format(user.username))
            flash(
                'Hello {}! You can now claim and manage your devices.'.format(
                    current_user.username), 'alert-success')
            return redirect(url_for('index'))
        else:
            logger.info('failed log in: {}'.format(user.username))
            flash('Invalid credentials', 'alert-danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logger.info('logging out: {}'.format(current_user.username))
    logout_user()
    flash('Logged out.', 'alert-info')
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_edit():
    # TODO: logging
    if request.method == 'POST':
        if current_user.auth(request.values.get('password', None)) is True:
            try:
                if request.form['new_password'] is not None and len(
                        request.form['new_password']) > 0:
                    current_user.password = request.form['new_password']
            except Exception as exc:
                if exc.args[0] == 'too_short':
                    flash('Password too short, minimum length is 3',
                          'alert-warning')
                else:
                    logger.error(exc)
            else:
                current_user.display_name = request.form['display_name']
                new_flags = request.form.getlist('flags')
                current_user.is_hidden = 'hidden' in new_flags
                current_user.is_name_anonymous = 'anonymous for public' in new_flags
                logger.info('flags: got {} set {:b}'.format(new_flags, current_user.flags))
                current_user.save()
                flash('Saved', 'alert-success')
        else:
            flash('Invalid password', 'alert-danger')

    return render_template('profile.html', user=current_user)
