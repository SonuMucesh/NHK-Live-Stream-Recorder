import unittest
import json
from unittest.mock import patch, mock_open
from main import use_config_to_set_variables


class TestMain(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "local_timezone": "Europe/London",
        "recording_path": "/path/to/recordings",
        "series_ids": ["series1", "series2"],
        "epg_url": "http://example.com/epg",
        "livestream_url": "http://example.com/livestream",
        "sonarr_integration": True,
        "sonarr_url": "http://example.com/sonarr",
        "sonarr_api_key": "sonarr_api_key",
        "series_ids_mapping": [{"nhk_series_id": "nhk1", "tv_db_id": "tvdb1"}],
        "ffmpeg_log_path": "/path/to/ffmpeg.log",
        "fuzzy_match_ratio": 85
    }))
    def test_use_config_to_set_variables_valid_config(self, mock_file):
        result = use_config_to_set_variables()
        self.assertTrue(result)

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "local_timezone": "Europe/London",
        "recording_path": "/path/to/recordings",
        "series_ids": ["series1", "series2"],
    }))
    def test_use_config_to_set_variables_missing_fields(self, mock_file):
        result = use_config_to_set_variables()
        self.assertFalse(result)

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({}))
    def test_use_config_to_set_variables_empty_config(self, mock_file):
        result = use_config_to_set_variables()
        self.assertFalse(result)

    @patch('builtins.open', new_callable=mock_open, read_data="not a valid json")
    def test_use_config_to_set_variables_invalid_json(self, mock_file):
        with self.assertRaises(json.JSONDecodeError):
            use_config_to_set_variables()


if __name__ == '__main__':
    unittest.main()
