#!/usr/bin/python3
import json
import logging
import os
from datetime import datetime

from flask import Flask, flash, render_template, redirect, url_for, request, \
    jsonify, abort
from flask_login import LoginManager, login_required, current_user, login_user, \
    logout_user

from whois import settings
from whois.database import db, Device, User
from whois.helpers import owners_from_devices, filter_hidden, \
    unclaimed_devices, filter_anon_names
from whois.mikrotik import parse_mikrotik_data

IP_MASK = '192.168.88.1-255'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get_by_id(user_id)
    except User.DoesNotExist as exc:
        logger.error('{}'.format(exc))
        logger.error('return None')
        return None


# TODO: taken from SO
def ip_range(mask, addr):
    splitted_ip = addr.split('.')
    for index, current_range in enumerate(mask.split('.')):
        if '-' in current_range:
            mini, maxi = map(int,current_range.split('-'))
        else:
            mini = maxi = int(current_range)
        if not (mini <= int(splitted_ip[index]) <= maxi):
            return False
    return True


@app.before_request
def before_request():
    logger.info('connecting to db')
    db.connect()
    if not ip_range(IP_MASK, request.remote_addr):
        flash('Outside local network, some functions forbidden!',
              'alert-warning')


@app.teardown_appcontext
def after_request(error):
    logger.info('closing db')
    db.close()
    if error:
        logger.error(error)


@app.route('/')
def index():
    """Serve list of people in hs, show panel for logged users"""
    recent = Device.get_recent(**settings.recent_time)
    visible_devices = filter_hidden(recent)
    users = filter_hidden(owners_from_devices(visible_devices))

    if current_user.is_authenticated:
        unclaimed = unclaimed_devices(recent)
        mine = current_user.devices
        return render_template('index.html', unclaimed=unclaimed,
                               recent=recent, my_devices=mine,
                               users=filter_anon_names(users),
                               headcount=len(users))

    return render_template('landing.html', users=filter_anon_names(users),
                           headcount=len(users),
                           unknowncount=len(unclaimed_devices(recent)))


@app.route('/api/now', methods=['GET'])
def now_at_space():
    """
    Send list of people currently in HS as JSON, only registred people,
    used by other services in HS,
    requests should be from hs3.pl domain or from HSWAN
    """
    devices = filter_hidden(Device.get_recent(**settings.recent_time))
    users = filter_hidden(owners_from_devices(devices))

    data = {"users": sorted(map(str, filter_anon_names(users))),
            "headcount": len(users),
            "unknown_devices": len(unclaimed_devices(devices))}

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

        if request.headers.get('User-Agent') == 'Mikrotik/6.x Fetch':
            logger.info('got data from mikrotik')
            data = json.loads(request.values.get('data', []))
            parsed_data = parse_mikrotik_data(datetime.now(), data)
        else:
            logger.warning('bad request \n{}'.format(request.headers))
            return abort(400)

        logger.info('parsed data, got {} devices'.format(len(parsed_data)))

        with db.atomic():
            for dev in parsed_data:
                Device.update_or_create(**dev)

        logger.info('updated last seen devices')

        return 'OK', 200
    else:
        logger.warning(
            'request from outside whitelist: {}'.format(request.remote_addr))
        return abort(403)


def set_device_flags(device, new_flags):
    if device.owner is not None and device.owner.get_id() != current_user.get_id():
        logger.error('no permission for {}'.format(current_user.username))
        flash('No permission!'.format(device.mac_address), 'alert-danger')
        return
    device.is_hidden = 'hidden' in new_flags
    device.is_esp = 'esp' in new_flags
    device.is_infrastructure = 'infrastructure' in new_flags
    print(device.flags)
    device.save()
    logger.info(
        '{} changed {} flags to {}'.format(current_user.username,
                                           device.mac_address, device.flags))
    flash('Flags set'.format(device.mac_address), 'alert-info')


@app.route('/device/<mac_address>', methods=['GET', 'POST'])
@login_required
def device(mac_address):
    """Get info about device, claim device, release device"""
    # TODO: dirty hack
    if not ip_range(IP_MASK, request.remote_addr):
        logger.error('{} request from outside'.format(request.remote_addr))
        abort(403)
    else:
        logger.info('{} is in allowed ip range'.format(request.remote_addr))

    try:
        device = Device.get(Device.mac_address == mac_address)
    except Device.DoesNotExist as exc:
        logger.error('{}'.format(exc))
        return abort(404)

    if request.method == 'POST':
        if request.values.get('action') == 'claim':
            claim_device(device)

        elif request.values.get('action') == 'unclaim':
            unclaim_device(device)
            set_device_flags(device, [])

        elif request.values.get('flags'):
            set_device_flags(device, request.form.getlist('flags'))

    return render_template('device.html', device=device)


def claim_device(device):
    if device.owner is not None:
        logger.error('no permission for {}'.format(current_user.username))
        flash('No permission!'.format(device.mac_address), 'alert-danger')
        return
    device.owner = current_user.get_id()
    device.save()
    logger.info(
        '{} claim {}'.format(current_user.username, device.mac_address))
    flash('Claimed {}!'.format(device.mac_address), 'alert-success')


def unclaim_device(device):
    if device.owner is not None and device.owner.get_id() != current_user.get_id():
        logger.error('no permission for {}'.format(current_user.username))
        flash('No permission!'.format(device.mac_address), 'alert-danger')
        return
    device.owner = None
    device.save()
    logger.info(
        '{} unclaim {}'.format(current_user.username, device.mac_address))
    flash('Unclaimed {}!'.format(device.mac_address), 'alert-info')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration form"""
    if request.method == 'POST':
        # TODO: WTF forms for safety
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
            logger.info('failed log in: {}'.format(None))
            flash('Invalid credentials', 'alert-danger')
            return render_template('login.html')

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

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info('logged out: {}'.format(username))
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
                logger.info('flags: got {} set {:b}'.format(new_flags,
                                                            current_user.flags))
                current_user.save()
                flash('Saved', 'alert-success')
        else:
            flash('Invalid password', 'alert-danger')

    return render_template('profile.html', user=current_user)
