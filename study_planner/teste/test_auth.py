import unittest
import sqlite3

from backend import Database, StudentRepo, AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        """Rulează înainte de FIECARE test. Pregătește o bază de date proaspătă în memorie."""
        self.db = Database()
        self.db.conn = sqlite3.connect(':memory:')  # Bază de date temporară în RAM
        self.db.create_tables()

        self.repo = StudentRepo(self.db)
        self.auth_service = AuthService(self.repo)

    def test_register_success(self):
        """Verifică dacă înregistrarea unui student funcționează corect."""
        result = self.auth_service.register("Miruna", "miruna@test.com", "parola123")
        self.assertTrue(result)

    def test_login_success(self):
        """Verifică dacă logarea funcționează cu date corecte."""
        self.auth_service.register("Miruna", "miruna@test.com", "parola123")
        result = self.auth_service.login("miruna@test.com", "parola123")
        self.assertTrue(result)
        self.assertEqual(self.auth_service.current_user['nume'], "Miruna")

    def test_login_fail_wrong_password(self):
        """Verifică dacă logarea este respinsă la o parolă greșită."""
        self.auth_service.register("Miruna", "miruna@test.com", "parola123")
        result = self.auth_service.login("miruna@test.com", "parolagresita")
        self.assertFalse(result)

    def tearDown(self):
        """Rulează după FIECARE test. Curăță resursele."""
        self.db.conn.close()