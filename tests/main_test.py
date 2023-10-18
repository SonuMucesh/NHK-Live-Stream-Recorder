import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import pytz
import main


class TestMain(unittest.TestCase):
    @patch('main.use_config_to_set_variables')
    @patch('main.get_epg_now')
    @patch('main.download_video')
    def test_main(self, mock_download_video, mock_get_epg_now, mock_use_config_to_set_variables):
        # Mock the use_config_to_set_variables function to return True
        mock_use_config_to_set_variables.return_value = True

        # Mock the get_epg_now function to do nothing
        mock_get_epg_now.return_value = None

        # Mock the download_video function to do nothing
        mock_download_video.return_value = None

        # Define a test program
        program = {
            "start_time": (datetime.now(pytz.UTC) + timedelta(seconds=5)).timestamp() * 1000,
            "end_time": (datetime.now(pytz.UTC) + timedelta(seconds=10)).timestamp() * 1000,
            "title": "Test Program"
        }

        # Set the global variable programs_to_download
        main.programs_to_download = [program]

        # Run the main function
        main.main()

        # Assert that the download_video function was called with the test program
        mock_download_video.assert_called_with(program)


if __name__ == '__main__':
    unittest.main()
