import unittest
import subprocess
import sys

class TestCLI(unittest.TestCase):
    def test_cli_help(self):
        result = subprocess.run([sys.executable, '-m', 'zoomtube.cli', '--help'], capture_output=True, text=True)
        self.assertIn('Usage', result.stdout)

    # Add more functional CLI tests here

if __name__ == "__main__":
    unittest.main()
