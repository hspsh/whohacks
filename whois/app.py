from __future__ import annotations

from datetime import datetime, timedelta
from logging import Logger

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

from whois.data.db.database import Database
from whois.data.repository.device_repository import DeviceRepository
from whois.data.repository.user_repository import UserRepository
from whois.entity.user import User, UserFlags
from whois.helpers import Helpers
from whois.settings.settings_template import AppSettings, MikrotikSettings


class WhoIs:

    def __init__(
        self,
        app_settings: AppSettings,
        mikrotik_settings: MikrotikSettings,
        database: Database,
        logger: Logger,
    ):
        self.logger = logger
        self.logger.debug("Initializing WhoIs...")

        self.app = Flask(__name__)
        self.cors = CORS(self.app, resources={r"/api/*": {"origins": "*"}})

        self.app_settings = app_settings
        self.mikrotik_settings = mikrotik_settings

        self.app.config.from_object(app_settings)
        self.app.config.from_object(mikrotik_settings)

        self.database = database
        self.user_repository = UserRepository(database)
        self.device_repository = DeviceRepository(database)

        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)

        self.helpers = Helpers(self.app_settings)

        self.add_rules()
        self.add_template_filters()
        self.register_routes()

        self.logger.debug("Initialized WhoIs")

        self.common_vars_tpl = {"app": self.app.config.get_namespace("APP_")}

        self.oauth = OAuth(self.app)
        if app_settings.OIDC_ENABLED:
            self.oauth.register(
                "sso",
                server_metadata_url=app_settings.APP_OAUTH_OPENID,
                client_kwargs={"scope": "openid profile email"},
            )

    def add_rules(self) -> None:
        self.login_manager.user_loader(self.load_user)
        self.app.before_request = self.before_request
        self.app.teardown_appcontext = self.after_request

    def add_template_filters(self) -> None:
        def local_time(dt: datetime):
            return dt.astimezone(self.app_settings.APP_TIMEZONE)

        self.app.add_template_filter(local_time, name="local_time")

    def register_routes(self) -> None:
        self.app.add_url_rule("/", view_func=self.index)
        self.app.add_url_rule("/devices", view_func=self.devices)
        self.app.add_url_rule("/api/now", view_func=self.now_at_space)
        self.app.add_url_rule(
            "/device",
            endpoint="<mac_address>",
            methods=["GET", "POST"],
            view_func=self.helpers.in_space_required(login_required(self.device_view)),
        )
        self.app.add_url_rule(
            "/register",
            methods=["GET", "POST"],
            view_func=self.helpers.in_space_required(self.register_form),
        )
        self.app.add_url_rule("/login", methods=["GET", "POST"], view_func=self.login)
        self.app.add_url_rule("/login/oauth", view_func=self.login_oauth)
        self.app.add_url_rule("/login/callback", view_func=self.callback)
        self.app.add_url_rule("/logout", view_func=login_required(self.logout))
        self.app.add_url_rule(
            "/profile",
            methods=["GET", "POST"],
            view_func=login_required(self.profile_edit),
        )

    # Rules for Flask App
    def load_user(self, user_id):
        try:
            return self.user_repository.get_by_id(user_id)
        except NoResultFound as exc:
            self.app.logger.error("{}".format(exc))
            return None

    def before_request(self):
        self.app.logger.info("connecting to db")
        self.database.connect()

        if request.headers.getlist("X-Forwarded-For"):
            ip_addr = request.headers.getlist("X-Forwarded-For")[0]
            self.logger.info(
                "forward from %s to %s",
                request.remote_addr,
                request.headers.getlist("X-Forwarded-For")[0],
            )
        else:
            ip_addr = request.remote_addr

        if not self.helpers.ip_range(self.app_settings.ip_mask, ip_addr):
            self.app.logger.error("%s", request.headers)
            flash("Outside local network, some functions forbidden!", "outside-warning")

    def after_request(self, error):
        if self.database.is_connected:
            self.app.logger.info("Closing the database connection")
            self.database.disconnect()
        else:
            self.app.logger.info("Database connection was already closed")

        if error:
            self.app.logger.error(error)

    # Routes for Flask App
    def index(self):
        """Serve list of people in hs, show panel for logged users"""
        self.logger.debug("Called '/'")
        devices = self.device_repository.get_all()
        recent = self.helpers.filter_recent(
            timedelta(**self.app_settings.RECENT_TIME), devices
        )
        visible_devices = self.helpers.filter_hidden(recent)
        users = self.helpers.filter_hidden(
            self.helpers.owners_from_devices(visible_devices)
        )

        return render_template(
            "landing.html",
            users=self.helpers.filter_anon_names(users),
            headcount=len(users),
            unknowncount=len(self.helpers.unclaimed_devices(recent)),
            **self.common_vars_tpl,
        )

    @login_required
    def devices(self):
        self.logger.debug("Called '/devices'")
        devices = self.device_repository.get_all()
        recent = self.helpers.filter_recent(
            timedelta(**self.app_settings.RECENT_TIME), devices
        )
        visible_devices = self.helpers.filter_hidden(recent)
        users = self.helpers.filter_hidden(
            self.helpers.owners_from_devices(visible_devices)
        )

        if current_user.is_authenticated:
            unclaimed = self.helpers.unclaimed_devices(recent)
            mine = self.device_repository.get_by_user_id(current_user.get_id())
            return render_template(
                "devices.html",
                unclaimed=unclaimed,
                recent=recent,
                my_devices=mine,
                users=self.helpers.filter_anon_names(users),
                headcount=len(users),
                **self.common_vars_tpl,
            )

    def now_at_space(self):
        """
        Send list of people currently in HS as JSON, only registred people,
        used by other services in HS,
        requests should be from hsp.sh domain or from HSWAN
        """
        self.logger.debug("Called '/api/now'")
        period = {**self.app_settings.RECENT_TIME}

        for key in ["days", "hours", "minutes"]:
            if key in request.args:
                period[key] = request.args.get(key, default=0, type=int)

        devices = self.device_repository.get_all()
        recent = self.helpers.filter_recent(
            timedelta(**self.app_settings.RECENT_TIME), devices
        )
        users = self.helpers.filter_hidden(self.helpers.owners_from_devices(recent))

        data = {
            "users": sorted(map(str, self.helpers.filter_anon_names(users))),
            "headcount": len(users),
            "unknown_devices": len(self.helpers.unclaimed_devices(recent)),
        }

        self.logger.info("sending request for /api/now {}".format(data))

        return jsonify(data)

    def set_device_flags(self, device, new_flags):
        if device.owner is not None and device.owner.get_id() != current_user.get_id():
            self.logger.error("no permission for {}".format(current_user.username))
            flash("No permission!".format(device.mac_address), "error")
            return
        device.is_hidden = "hidden" in new_flags
        device.is_esp = "esp" in new_flags
        device.is_infrastructure = "infrastructure" in new_flags
        print(device.flags)
        device.save()
        self.logger.info(
            "{} changed {} flags to {}".format(
                current_user.username, device.mac_address, device.flags
            )
        )
        flash("Flags set".format(device.mac_address), "info")

    def device_view(self, mac_address):
        """Get info about device, claim device, release device"""
        self.logger.debug("Called '/device'")
        try:
            device = self.device_repository.get_by_mac_address(mac_address)
        except NoResultFound as exc:
            self.logger.error("{}".format(exc))
            return abort(404)

        if request.method == "POST":
            if request.values.get("action") == "claim":
                self.claim_device(device)

            elif request.values.get("action") == "unclaim":
                self.unclaim_device(device)
                self.set_device_flags(device, [])

            elif request.values.get("flags"):
                self.set_device_flags(device, request.form.getlist("flags"))

        return render_template("device.html", device=device, **self.common_vars_tpl)

    def claim_device(self, device):
        if device.owner is not None:
            self.logger.error("no permission for {}".format(current_user.username))
            flash("No permission!".format(device.mac_address), "error")
            return
        device.owner = current_user.get_id()
        device.save()
        self.logger.info(
            "{} claim {}".format(current_user.username, device.mac_address)
        )
        flash("Claimed {}!".format(device.mac_address), "success")

    def unclaim_device(self, device):
        if device.owner is not None and device.owner.get_id() != current_user.get_id():
            self.logger.error("no permission for {}".format(current_user.username))
            flash("No permission!".format(device.mac_address), "error")
            return
        device.owner = None
        device.save()
        self.logger.info(
            "{} unclaim {}".format(current_user.username, device.mac_address)
        )
        flash("Unclaimed {}!".format(device.mac_address), "info")

    def register_form(self):
        """Registration form"""
        self.logger.debug("Called '/register'")
        if current_user.is_authenticated:
            self.logger.error("Shouldn't register when auth")
            flash("Shouldn't register when auth", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            # TODO: WTF forms for safety
            display_name = request.form["display_name"]
            username = request.form["username"]
            password = request.form["password"]

            try:
                user = self.register(username, password, display_name)
            except Exception as exc:
                if exc.args[0] == "too_short":
                    flash("Password too short, minimum length is 3")
                else:
                    print(exc)
            else:
                self.logger.info("registered new user: {}".format(user.username))
                flash("Registered.", "info")

            return redirect(url_for("login"))

        return render_template("register.html", **self.common_vars_tpl)

    def login(self):
        """Login using query to DB or SSO"""
        self.logger.debug("Called '/login'")

        if current_user.is_authenticated:
            self.logger.error("Shouldn't login when auth")
            flash("You are already logged in", "error")
            return redirect(url_for("devices"))

        if request.method == "POST":
            try:
                username = request.form["username"]
                user = self.user_repository.get_by_username(username)
            except NoResultFound:
                user = None

            if user:
                if user.is_sso and self.app_settings.OIDC_ENABLED:
                    # User created via sso -> redirect to sso login
                    self.logger.info("Redirect to SSO user: {}".format(user.username))
                    return redirect(url_for("login_oauth"))
                elif user.auth(request.form["password"]):
                    # User password hash match -> login user successfully
                    login_user(user)
                    self.logger.info("logged in: {}".format(user.username))
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
                self.logger.info("failed log in: {}".format(request.form["username"]))
                flash("Invalid credentials", "error")

        return render_template(
            "login.html",
            oauth_enabled=self.app_settings.OIDC_ENABLED,
            **self.common_vars_tpl,
        )

    def login_oauth(self):
        self.logger.debug("Called '/login/oauth'")
        redirect_uri = url_for("callback", _external=True)
        return self.oauth.sso.authorize_redirect(redirect_uri)

    def callback(self):
        self.logger.debug("Called '/login/callback'")
        token = self.oauth.sso.authorize_access_token()
        user_info = self.oauth.sso.parse_id_token(token)
        if user_info:
            try:
                user = self.user_repository.get_by_username(
                    user_info["preferred_username"]
                )
            except NoResultFound:
                username = user_info["preferred_username"]
                self.logger.info(
                    f"No SSO-loggined user: {username}.\n" f"Register user {username}",
                )
                user = self.register_from_sso(username=username, display_name=username)

            if user is not None:
                login_user(user)
                self.logger.info("logged in: {}".format(user.username))
                flash(
                    "Hello {}! You can now claim and manage your devices.".format(
                        current_user.username
                    ),
                    "success",
                )
                return redirect(url_for("devices"))
            else:
                self.logger.info(
                    "failed log in: {}".format(user_info["preferred_username"])
                )
                flash("Invalid credentials", "error")
        return redirect(url_for("login"))

    def logout(self):
        self.logger.debug("Called '/logout'")
        username = current_user.username
        logout_user()
        self.app.logger.info("logged out: {}".format(username))
        flash("Logged out.", "info")
        return redirect(url_for("index"))

    def profile_edit(self):
        # TODO: logging
        self.logger.debug("Called '/profile'")
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
                        self.logger.error(exc)
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

                    self.logger.info(
                        "flags: got {} set {:b}".format(new_flags, current_user.flags)
                    )
                    self.user_repository.update(current_user)

                    flash("Saved", "success")
            else:
                flash("Invalid password", "error")

        return render_template(
            "profile.html", user=current_user, **self.common_vars_tpl
        )

    def register(self, username, password, display_name=None):
        """
        Creates user and hashes his password
        :param username: used in login
        :param password: plain text to be hashed
        :param display_name: displayed username
        :return: user instance
        """
        user = User(username=username, display_name=display_name)
        user.password = password
        self.user_repository.insert(user)
        return user

    def register_from_sso(self, username, display_name=None):
        """
        Creates user without any password. Such users can only login via SSO.
        :param username: used in login
        :param display_name: displayed username
        :return: user instance
        """
        user = User(username=username, display_name=display_name)
        self.user_repository.insert(user)
        return user
