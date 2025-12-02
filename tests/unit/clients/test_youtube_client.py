import unittest
from zoomtube.clients.youtube_client import YoutubeClient

class TestYoutubeClient(unittest.TestCase):
    def setUp(self):
        self.client = YoutubeClient()

    def test_initialization(self):
        self.assertIsInstance(self.client, YoutubeClient)

    # Add more tests for YoutubeClient methods here

if __name__ == "__main__":
    unittest.main()
