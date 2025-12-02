import unittest
from zoomtube.clients.zoom_client import ZoomClient

class TestZoomClient(unittest.TestCase):
    def setUp(self):
        self.client = ZoomClient()

    def test_initialization(self):
        self.assertIsInstance(self.client, ZoomClient)

    # Add more tests for ZoomClient methods here

if __name__ == "__main__":
    unittest.main()
