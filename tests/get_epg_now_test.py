import datetime
import unittest
from unittest.mock import patch
import pytz
import main
from main import get_epg_now


class TestGetEpgNow(unittest.TestCase):
    @patch('requests.get')
    @patch('main.SERIES_IDS', ["123", "456"])
    @patch.dict('main.SERIES_IDS_MAPPING', {"123": "abc", "456": "def"})
    def test_get_epg_now(self, mock_get):
        # Mock the API response
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            "channel": {
                "item": [
                    {
                        "seriesId": "123",
                        "airingId": "000",
                        "title": "NHK NEWSLINE",
                        "description": "NHK WORLD-JAPAN's flagship hourly news program delivers the latest world news, business and weather, with a focus on Japan and the rest of Asia.",
                        "link": "/nhkworld/en/news/",
                        "pubDate": "1697641200000",
                        "endDate": int(datetime.datetime.now().timestamp()),
                        "jstrm": "1",
                        "wstrm": "1",
                        "subtitle": "",
                        "content": "",
                        "content_clean": "",
                        "pgm_gr_id": "",
                        "thumbnail": "/nhkworld/upld/thumbnails/en/tv/regular_program/6b19d5ca38c0e4c7b4c78cb18f17cbd6_large.jpg",
                        "thumbnail_s": "/nhkworld/upld/thumbnails/en/tv/regular_program/6b19d5ca38c0e4c7b4c78cb18f17cbd6_small.jpg",
                        "showlist": "1",
                        "internal": "0",
                        "genre": {
                            "TV": "11",
                            "Top": "",
                            "LC": ""
                        },
                        "vod_id": "",
                        "vod_url": "",
                        "analytics": "[nhkworld]simul;NHK NEWSLINE;w02,001;1001-000-2023;2023-10-19T00:00:00+09:00"
                    }
                ]
            }
        }

        # Mock cached_schedule
        with patch.object(main, 'cached_schedule', new=mock_response.json.return_value["channel"]["item"]):
            EPG_URL = ''
            HEADERS = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
                'Accept': '*/*',
                'Accept-Language': 'en-GB,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www3.nhk.or.jp/',
                'Origin': 'https://www3.nhk.or.jp',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site'
            }

            # Call the function
            get_epg_now()

            # Assert that the API was called with the correct URL
            mock_get.assert_called_once_with(EPG_URL, headers=HEADERS)

    @patch('requests.get')
    @patch('main.SERIES_IDS', ["123", "456"])
    @patch.dict('main.SERIES_IDS_MAPPING', {"123": "abc", "456": "def"})
    @patch('main.LOCAL_TIMEZONE', pytz.timezone('Europe/London'))
    @patch('time.sleep', return_value=None)
    def test_get_epg_now_with_no_programs_found(self, mock_sleep, mock_get):
        # Mock the API response
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            "channel": {
                "item": [
                    {
                        "seriesId": "122223",
                        "airingId": "000",
                        "title": "NHK NEWSLINE",
                        "description": "NHK WORLD-JAPAN's flagship hourly news program delivers the latest world news, business and weather, with a focus on Japan and the rest of Asia.",
                        "link": "/nhkworld/en/news/",
                        "pubDate": "1697641200000",
                        "endDate": int(datetime.datetime.now().timestamp() + 10) * 1000,
                        "jstrm": "1",
                        "wstrm": "1",
                        "subtitle": "",
                        "content": "",
                        "content_clean": "",
                        "pgm_gr_id": "",
                        "thumbnail": "/nhkworld/upld/thumbnails/en/tv/regular_program/6b19d5ca38c0e4c7b4c78cb18f17cbd6_large.jpg",
                        "thumbnail_s": "/nhkworld/upld/thumbnails/en/tv/regular_program/6b19d5ca38c0e4c7b4c78cb18f17cbd6_small.jpg",
                        "showlist": "1",
                        "internal": "0",
                        "genre": {
                            "TV": "11",
                            "Top": "",
                            "LC": ""
                        },
                        "vod_id": "",
                        "vod_url": "",
                        "analytics": "[nhkworld]simul;NHK NEWSLINE;w02,001;1001-000-2023;2023-10-19T00:00:00+09:00"
                    }
                ]
            }
        }

        # Mock cached_schedule
        with patch.object(main, 'cached_schedule', new=mock_response.json.return_value["channel"]["item"]):
            # Call the function
            try:
                get_epg_now()
            except Exception as e:
                pass

            # Assert that sleep was called at least once
            assert mock_sleep.call_count >= 1


if __name__ == '__main__':
    unittest.main()
