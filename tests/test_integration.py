import logging
from unittest import TestCase

from whois.app import WhohacksApp
from whois.data.db.database import Database
from whois.settings.testing import app_settings, mikrotik_settings


class ApiTestCase(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            format="%(asctime)s %(module)s %(levelname)s: %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
            level=logging.DEBUG,
            force=True,
        )
        self.logger.addHandler(logging.FileHandler(f"{__name__}.log"))

        self.db = Database("sqlite:///whohacks.test.sqlite")
        self.db.drop()
        self.db.create_db()
        self.whois = WhohacksApp(app_settings, mikrotik_settings, self.db, self.logger)
        self.app = self.whois.app.test_client()
        self.app.testing = True

    def test_index(self):
        """User should be able to access the index page"""
        response = self.app.get("/")

        assert (
            response.status_code == 200
        ), f"Actual response code: {response.status_code}"

    def test_login_page(self):
        """User should be able to access login page"""
        response = self.app.get("/login")

        assert (
            response.status_code == 200
        ), f"Actual response code: {response.status_code}"

    def test_register_page(self):
        """User should be able to access the register page"""
        response = self.app.get("/register")

        assert (
            response.status_code == 200
        ), f"Actual response code: {response.status_code}"

    def test_login_fail(self):
        """User shouldn't be able to login into an non-existent account"""
        response = self.app.post("/login", data={"username": "i_dont_exist"})

        assert (
            response.status_code == 200
        ), f"Actual response code: {response.status_code}"

        response_body = response.get_data(as_text=True)

        assert "Please login" in response_body, "'Please login' not in response body"

        assert (
            "Invalid credentials" in response_body
        ), "'Invalid credentials' should be in the response body"

    def test_register_login(self):
        """User should be able to register and login into created account"""
        register_response = self.app.post(
            "/register",
            data={
                "display_name": "test_user",
                "username": "test_user",
                "password": "test123",
            },
        )

        assert (
            register_response.status_code == 302
        ), f"Actual response code: {register_response.status_code}"

        login_response = self.app.post(
            "/login",
            data={
                "username": "test_user",
                "password": "test123",
            },
        )

        assert (
            login_response.status_code == 302
        ), f"Actual response code: {login_response.status_code}"
