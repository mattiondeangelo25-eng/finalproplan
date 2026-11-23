import sqlite3
import tempfile
import unittest
from pathlib import Path

from werkzeug.security import check_password_hash

from app import create_app


class SignupTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database = str(Path(self.temp_dir.name) / "test.sqlite")
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "DATABASE": database,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registration_confirms_and_redirects_to_main_app(self):
        response = self.client.post(
            "/signup",
            data={"email": "Reader@Example.com", "password": "secure-pass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        page = self.client.get(response.headers["Location"])
        self.assertIn(b"Registration successful. Welcome!", page.data)
        self.assertIn(b"reader@example.com", page.data)

    def test_registration_stores_password_hash(self):
        self.client.post(
            "/signup",
            data={"email": "reader@example.com", "password": "secure-pass"},
        )

        with self.app.app_context():
            with sqlite3.connect(self.app.config["DATABASE"]) as connection:
                password_hash = connection.execute(
                    "SELECT password_hash FROM users WHERE email = ?",
                    ("reader@example.com",),
                ).fetchone()[0]

        self.assertNotEqual(password_hash, "secure-pass")
        self.assertTrue(check_password_hash(password_hash, "secure-pass"))

    def test_invalid_email_is_rejected(self):
        response = self.client.post(
            "/signup", data={"email": "not-an-email", "password": "secure-pass"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Enter a valid email address.", response.data)

    def test_malformed_domain_is_rejected(self):
        response = self.client.post(
            "/signup",
            data={"email": "reader@example..com", "password": "secure-pass"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Enter a valid email address.", response.data)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        data = {"email": "reader@example.com", "password": "secure-pass"}
        self.client.post("/signup", data=data)
        self.client.post("/logout")
        response = self.client.post(
            "/signup",
            data={"email": "READER@example.com", "password": "secure-pass"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"An account with that email already exists.", response.data)


if __name__ == "__main__":
    unittest.main()
