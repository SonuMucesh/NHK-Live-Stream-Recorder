import subprocess
import unittest
from unittest.mock import patch, mock_open, MagicMock
from main import download_video


class TestDownloadVideo(unittest.TestCase):
    @patch('os.path.join', return_value='mock_path')
    @patch('main.subprocess.Popen')
    @patch('main.LIVESTREAM_URL', new_callable=MagicMock(return_value='mock_url'))
    def test_download_video(self, mock_url, mock_popen, mock_os_path_join):
        mock_process = MagicMock()
        mock_process.stdout = ['mock_output']
        mock_popen.return_value = mock_process

        mock_file = mock_open()
        with patch('main.open', mock_file):
            program = {
                'duration': '10',
                'sonarr_episode_name': None,
                'subtitle': 'mock_subtitle',
                'title': 'mock_title',
                'description': 'mock_description'
            }
            download_video(program)

        mock_os_path_join.assert_called()
        mock_popen.assert_called_with(
            ['ffmpeg', '-i', 'mock_url', '-t', '10', '-c', 'copy', '-metadata', 'description=mock_description',
             'mock_path'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        mock_file().write.assert_called_with('mock_output')
        mock_process.wait.assert_called()


if __name__ == '__main__':
    unittest.main()
