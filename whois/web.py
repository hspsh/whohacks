import logging
from datetime import datetime, timedelta, timezone

from authlib.integrations.flask_client import OAuth
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_cors import CORS
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy.orm.exc import NoResultFound

from whois import settings
from whois.data.db.database import Database
from whois.data.repository.device_repository import DeviceRepository
from whois.data.repository.user_repository import UserRepository
from whois.entity.user import User, UserFlags
from whois.helpers import (
    filter_anon_names,
    filter_hidden,
    filter_recent,
    in_space_required,
    ip_range,
    owners_from_devices,
    unclaimed_devices,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object("whois.settings")
login_manager = LoginManager()
login_manager.init_app(app)
database = Database()
device_repository = DeviceRepository(database)
user_repository = UserRepository(database)

if settings.oidc_enabled:
    oauth = OAuth(app)
    oauth.register(
        "sso",
        server_metadata_url=settings.APP_OAUTH_OPENID,
        client_kwargs={"scope": "openid profile email"},
    )


cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

common_vars_tpl = {"app": app.config.get_namespace("APP_")}


@app.template_filter("local_time")
def local_time(dt: datetime):
    return dt.astimezone(settings.APP_TIMEZONE)


@login_manager.user_loader
def load_user(user_id):
    try:
        return user_repository.get_by_id(user_id)
    except NoResultFound as exc:
        app.logger.error("{}".format(exc))
        return None


@app.before_request
def before_request():
    app.logger.info("connecting to db")
    database.connect()

    if request.headers.getlist("X-Forwarded-For"):
        ip_addr = request.headers.getlist("X-Forwarded-For")[0]
        logger.info(
            "forward from %s to %s",
            request.remote_addr,
            request.headers.getlist("X-Forwarded-For")[0],
        )
    else:
        ip_addr = request.remote_addr

    if not ip_range(settings.ip_mask, ip_addr):
        app.logger.error("%s", request.headers)
        flash("Outside local network, some functions forbidden!", "outside-warning")


@app.teardown_appcontext
def after_request(error):
    if database.is_connected:
        app.logger.info("Closing the database connection")
        database.disconnect()
    else:
        app.logger.info("Database connection was already closed")

    if error:
        app.logger.error(error)


@app.route("/")
def index():
    """Serve list of people in hs, show panel for logged users"""
    devices = device_repository.get_all()
    recent = filter_recent(timedelta(**settings.recent_time), devices)
    visible_devices = filter_hidden(recent)
    users = filter_hidden(owners_from_devices(visible_devices))

    return render_template(
        "landing.html",
        users=filter_anon_names(users),
        headcount=len(users),
        unknowncount=len(unclaimed_devices(recent)),
        **common_vars_tpl,
    )


@login_required
@app.route("/devices")
def devices():
    devices = device_repository.get_all()
    recent = filter_recent(timedelta(**settings.recent_time), devices)
    visible_devices = filter_hidden(recent)
    users = filter_hidden(owners_from_devices(visible_devices))

    if current_user.is_authenticated:
        unclaimed = unclaimed_devices(recent)
        mine = filter(lambda device: device.owner == current_user.get_id(), devices)
        return render_template(
            "devices.html",
            unclaimed=unclaimed,
            recent=recent,
            my_devices=mine,
            users=filter_anon_names(users),
            headcount=len(users),
            **common_vars_tpl,
        )


@app.route("/api/now", methods=["GET"])
def now_at_space():
    """
    Send list of people currently in HS as JSON, only registred people,
    used by other services in HS,
    requests should be from hsp.sh domain or from HSWAN
    """
    period = {**settings.recent_time}

    for key in ["days", "hours", "minutes"]:
        if key in request.args:
            period[key] = request.args.get(key, default=0, type=int)

    devices = device_repository.get_all()
    recent = filter_recent(timedelta(**settings.recent_time), devices)
    users = filter_hidden(owners_from_devices(recent))

    data = {
        "users": sorted(map(str, filter_anon_names(users))),
        "headcount": len(users),
        "unknown_devices": len(unclaimed_devices(recent)),
    }

    app.logger.info("sending request for /api/now {}".format(data))

    return jsonify(data)


def set_device_flags(device, new_flags):
    if device.owner is not None and device.owner.get_id() != current_user.get_id():
        app.logger.error("no permission for {}".format(current_user.username))
        flash("No permission!".format(device.mac_address), "error")
        return
    device.is_hidden = "hidden" in new_flags
    device.is_esp = "esp" in new_flags
    device.is_infrastructure = "infrastructure" in new_flags
    print(device.flags)
    device.save()
    app.logger.info(
        "{} changed {} flags to {}".format(
            current_user.username, device.mac_address, device.flags
        )
    )
    flash("Flags set".format(device.mac_address), "info")


@app.route("/device/<mac_address>", methods=["GET", "POST"])
@login_required
@in_space_required()
def device_view(mac_address):
    """Get info about device, claim device, release device"""

    try:
        device = device_repository.get_by_mac_address(mac_address)
    except NoResultFound as exc:
        app.logger.error("{}".format(exc))
        return abort(404)

    if request.method == "POST":
        if request.values.get("action") == "claim":
            claim_device(device)

        elif request.values.get("action") == "unclaim":
            unclaim_device(device)
            set_device_flags(device, [])

        elif request.values.get("flags"):
            set_device_flags(device, request.form.getlist("flags"))

    return render_template("device.html", device=device, **common_vars_tpl)


def claim_device(device):
    if device.owner is not None:
        app.logger.error("no permission for {}".format(current_user.username))
        flash("No permission!".format(device.mac_address), "error")
        return
    device.owner = current_user.get_id()
    device.save()
    app.logger.info("{} claim {}".format(current_user.username, device.mac_address))
    flash("Claimed {}!".format(device.mac_address), "success")


def unclaim_device(device):
    if device.owner is not None and device.owner.get_id() != current_user.get_id():
        app.logger.error("no permission for {}".format(current_user.username))
        flash("No permission!".format(device.mac_address), "error")
        return
    device.owner = None
    device.save()
    app.logger.info("{} unclaim {}".format(current_user.username, device.mac_address))
    flash("Unclaimed {}!".format(device.mac_address), "info")


@app.route("/register", methods=["GET", "POST"])
@in_space_required()
def register():
    """Registration form"""
    if current_user.is_authenticated:
        app.logger.error("Shouldn't register when auth")
        flash("Shouldn't register when auth", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        # TODO: WTF forms for safety
        display_name = request.form["display_name"]
        username = request.form["username"]
        password = request.form["password"]

        try:
            user = register(username, password, display_name)
        except Exception as exc:
            if exc.args[0] == "too_short":
                flash("Password too short, minimum length is 3")
            else:
                print(exc)
        else:
            app.logger.info("registered new user: {}".format(user.username))
            flash("Registered.", "info")

        return redirect(url_for("login"))

    return render_template("register.html", **common_vars_tpl)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login using query to DB or SSO"""
    if current_user.is_authenticated:
        app.logger.error("Shouldn't login when auth")
        flash("You are already logged in", "error")
        return redirect(url_for("devices"))

    if request.method == "POST":
        try:
            username = request.form["username"]
            user = user_repository.get_by_username(username)
        except NoResultFound:
            user = None

        if user:
            if user.is_sso:
                # User created via sso -> redirect to sso login
                app.logger.info("Redirect to SSO user: {}".format(user.username))
                return redirect(url_for("login_oauth"))
            elif user.auth(request.form["password"]):
                # User password hash match -> login user successfully
                login_user(user)
                app.logger.info("logged in: {}".format(user.username))
            else:
                pass

        if current_user.is_authenticated:
            flash(
                "Hello {}! You can now claim and manage your devices.".format(
                    current_user.username
                ),
                "success",
            )
            return redirect(url_for("devices"))
        else:
            app.logger.info("failed log in: {}".format(request.form["username"]))
            flash("Invalid credentials", "error")

    return render_template(
        "login.html", oauth_enabled=settings.oidc_enabled, **common_vars_tpl
    )


@app.route("/login/oauth")
def login_oauth():
    redirect_uri = url_for("callback", _external=True)
    return oauth.sso.authorize_redirect(redirect_uri)


@app.route("/login/callback")
def callback():
    token = oauth.sso.authorize_access_token()
    user_info = oauth.sso.parse_id_token(token)
    if user_info:
        try:
            user = user_repository.get_by_username(user_info["preferred_username"])
        except NoResultFound:
            username = user_info["preferred_username"]
            app.logger.info(
                f"No SSO-loggined user: {username}.\n" f"Register user {username}",
            )
            user = register_from_sso(username=username, display_name=username)

        if user is not None:
            login_user(user)
            app.logger.info("logged in: {}".format(user.username))
            flash(
                "Hello {}! You can now claim and manage your devices.".format(
                    current_user.username
                ),
                "success",
            )
            return redirect(url_for("devices"))
        else:
            app.logger.info("failed log in: {}".format(user_info["preferred_username"]))
            flash("Invalid credentials", "error")
    return redirect(url_for("login"))


@app.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    app.logger.info("logged out: {}".format(username))
    flash("Logged out.", "info")
    return redirect(url_for("index"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_edit():
    # TODO: logging
    if request.method == "POST":
        if current_user.auth(request.values.get("password", None)) is True:
            try:
                if (
                    request.form["new_password"] is not None
                    and len(request.form["new_password"]) > 0
                ):
                    current_user.password = request.form["new_password"]
            except Exception as exc:
                if exc.args[0] == "too_short":
                    flash("Password too short, minimum length is 3", "warning")
                else:
                    app.logger.error(exc)
            else:
                current_user.display_name = request.form["display_name"]
                new_flags = request.form.getlist("flags")
                if "hidden" in new_flags:
                    current_user.flags.set_flag(UserFlags.is_hidden.value)
                else:
                    current_user.flags.unset_flag(UserFlags.is_hidden.value)

                if "anonymous for public" in new_flags:
                    current_user.flags.set_flag(UserFlags.is_name_anonymous.value)
                else:
                    current_user.flags.unset_flag(UserFlags.is_name_anonymous.value)

                app.logger.info(
                    "flags: got {} set {:b}".format(new_flags, current_user.flags)
                )
                user_repository.update(current_user)

                flash("Saved", "success")
        else:
            flash("Invalid password", "error")

    return render_template("profile.html", user=current_user, **common_vars_tpl)


def register(username, password, display_name=None):
    """
    Creates user and hashes his password
    :param username: used in login
    :param password: plain text to be hashed
    :param display_name: displayed username
    :return: user instance
    """
    user = User(username=username, display_name=display_name)
    user.password = password
    user_repository.insert(user)
    return user


def register_from_sso(username, display_name=None):
    """
    Creates user without any password. Such users can only login via SSO.
    :param username: used in login
    :param display_name: displayed username
    :return: user instance
    """
    user = User(username=username, display_name=display_name)
    user_repository.insert(user)
    return user
