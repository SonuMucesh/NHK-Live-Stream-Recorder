import unittest
from unittest.mock import patch
import main


class TestSonarr(unittest.TestCase):
    @patch('main.SonarrAPI')
    @patch('main.fuzzy_match')
    def test_sonarr(self, mock_fuzzy_match, mock_sonarr_api):
        # Mock the program data
        program = {
            "title": "Test Title",
            "subtitle": "Test Episode",
            "pubDate": "1715721600",
            "seriesId": "12345"
        }

        # Mock the SERIES_IDS_MAPPING constant
        main.SERIES_IDS_MAPPING = {"12345": "67890"}

        # Mock the FUZZY_MATCH_RATIO constant
        main.FUZZY_MATCH_RATIO = 85

        # Mock the SonarrAPI.get_series method
        mock_sonarr_api.get_series.return_value = [{"id": "67890"}]

        # Mock the SonarrAPI.get_episode method
        mock_sonarr_api.get_episode.return_value = [
            {
                "title": "Test Episode",
                "airDateUtc": "2023-18-30T20:00:00Z",
                "hasFile": False
            }
        ]

        # Mock the fuzzy_match function
        mock_fuzzy_match.return_value = 90

        # Call the sonarr function
        try:
            main.sonarr(program)
        except Exception as e:
            pass

        mock_fuzzy_match.assert_called_with(program, mock_sonarr_api.get_episode.return_value[0])


if __name__ == '__main__':
    unittest.main()
