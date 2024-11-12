import logging
import sys
from unittest import TestCase

from flask_login import LoginManager

from whois.app import WhoIs
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
        self.whois = WhoIs(app_settings, mikrotik_settings, self.db, self.logger)
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
