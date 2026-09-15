import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

class AppTests(unittest.TestCase):
    def test_search_renders_without_credentials(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        app.text_input[0].set_value('computer science')
        app.multiselect[0].set_value(['Germany', 'USA'])
        app.selectbox[0].set_value("Master's")
        app.button[0].click().run(timeout=20)
        self.assertEqual(len(app.exception), 0)
        self.assertIn('match_score', app.session_state['results'].columns)
