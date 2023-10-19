import unittest
from unittest.mock import patch
from main import store_programs_to_download


class TestStoreProgramsToDownload(unittest.TestCase):
    def setUp(self):
        self.program = {
            "title": "Test Title",
            "subtitle": "Test Subtitle",
            "pubDate": "2022-01-01T00:00:00Z",
            "endDate": "2022-01-01T01:00:00Z",
            "description": "Test Description"
        }
        self.sonarr_episode_name = "Test Episode"

    @patch('builtins.print')
    def test_store_programs_to_download(self, mock_print):
        # Assume
        programs_to_download = [
            {
                "title": "Test Title",
                "subtitle": "Test Subtitle",
                "start_time": "2022-01-01T00:00:00Z",
                "end_time": "2022-01-01T01:00:00Z",
                "description": "Test Description",
                "duration": None,
                "sonarr_episode_name": "Test Episode"
            },
        ]

        # Action
        store_programs_to_download(self.program, self.sonarr_episode_name)

        # Assert
        self.assertEqual(len(programs_to_download), 1)
        self.assertEqual(programs_to_download[0]['title'], self.program['title'])
        self.assertEqual(programs_to_download[0]['subtitle'], self.program['subtitle'])
        self.assertEqual(programs_to_download[0]['start_time'], self.program['pubDate'])
        self.assertEqual(programs_to_download[0]['end_time'], self.program['endDate'])
        self.assertEqual(programs_to_download[0]['description'], self.program['description'])
        self.assertEqual(programs_to_download[0]['sonarr_episode_name'], self.sonarr_episode_name)

    @patch('builtins.print')
    def test_store_programs_to_download_duplicate(self, mock_print):
        # Assume
        programs_to_download = [{
            "title": "Test Title",
            "subtitle": "Test Subtitle",
            "start_time": "2022-01-01T00:00:00Z",
            "end_time": "2022-01-01T01:00:00Z",
            "description": "Test Description",
            "duration": None,
            "sonarr_episode_name": "Test Episode"
        }]

        # Action
        store_programs_to_download(self.program, self.sonarr_episode_name)

        # Assert
        self.assertEqual(len(programs_to_download), 1)


if __name__ == '__main__':
    unittest.main()
