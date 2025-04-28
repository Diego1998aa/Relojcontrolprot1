import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys

# Add project directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import RelojControlApp

class TestRelojControlApp(unittest.TestCase):
    def setUp(self):
        # Patch tkinter image loading to avoid TclError
        patcher_img = patch('customtkinter.CTkImage.__init__', return_value=None)
        patcher_img.start()
        self.addCleanup(patcher_img.stop)

        self.app = RelojControlApp()
        # Patch messagebox to avoid actual GUI popups during tests
        patcher_info = patch('tkinter.messagebox.showinfo')
        self.mock_showinfo = patcher_info.start()
        self.addCleanup(patcher_info.stop)
        patcher_warn = patch('tkinter.messagebox.showwarning')
        self.mock_showwarning = patcher_warn.start()
        self.addCleanup(patcher_warn.stop)
        patcher_error = patch('tkinter.messagebox.showerror')
        self.mock_showerror = patcher_error.start()
        self.addCleanup(patcher_error.stop)

    def test_load_users_no_error(self):
        try:
            self.app.load_users()
        except Exception as e:
            self.fail(f"load_users raised Exception unexpectedly: {e}")

    def test_add_user_missing_fields(self):
        self.app.user_id = MagicMock()
        self.app.user_name = MagicMock()
        self.app.user_role = MagicMock()
        self.app.user_id.get.return_value = ''
        self.app.user_name.get.return_value = ''
        self.app.user_role.get.return_value = ''
        self.app.add_user()
        self.mock_showwarning.assert_called_once()

    def test_add_user_existing_id(self):
        self.app.user_id = MagicMock()
        self.app.user_name = MagicMock()
        self.app.user_role = MagicMock()
        self.app.user_id.get.return_value = '12345678-9'
        self.app.user_name.get.return_value = 'Test User'
        self.app.user_role.get.return_value = 'Empleado'

        # Patch pandas read_csv to simulate existing user
        with patch('pandas.read_csv') as mock_read_csv, \
             patch('pandas.DataFrame.to_excel') as mock_to_excel:
            mock_read_csv.return_value = pd.DataFrame({
                'ID': ['12345678-9'],
                'Nombre': ['Existing User'],
                'Rol': ['Empleado'],
                'Huella': ['']
            })
            self.app.add_user()
            self.mock_showerror.assert_called_once()

    def test_register_fingerprint_no_user_id(self):
        self.app.user_id = MagicMock()
        self.app.user_id.get.return_value = ''
        self.app.register_fingerprint()
        self.mock_showwarning.assert_called_once()

if __name__ == '__main__':
    unittest.main()
