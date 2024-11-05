from unittest import TestCase

from whois.web import app


class ApiTestCase(TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        """User should be able to access the index page"""
        response = self.app.get("/")
        assert (
            response.status_code == 200
        ), f"Actual response code: {response.status_code}"
