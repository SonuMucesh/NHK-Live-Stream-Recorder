import unittest
from main import check_if_duplicate


class TestCheckIfDuplicate(unittest.TestCase):
    def setUp(self):
        self.series = {'title': 'Test Series'}
        self.episode_with_file = {'hasFile': True, 'seasonNumber': 1, 'episodeNumber': 1, 'title': 'Test Episode'}
        self.episode_without_file = {'hasFile': False, 'seasonNumber': 1, 'episodeNumber': 1, 'title': 'Test Episode'}

    def test_check_if_duplicate_with_file(self):
        result = check_if_duplicate(self.series, self.episode_with_file)
        self.assertEqual(result, False)

    def test_check_if_duplicate_without_file(self):
        result = check_if_duplicate(self.series, self.episode_without_file)
        expected_result = 'Test Series - 1x1 - Test Episode'
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
