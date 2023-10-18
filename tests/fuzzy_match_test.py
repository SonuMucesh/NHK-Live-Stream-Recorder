import unittest
from main import fuzzy_match


class TestFuzzyMatch(unittest.TestCase):
    def test_fuzzy_match(self):
        program = {'subtitle': 'Hello World'}
        episode = {'title': 'Hello World'}
        self.assertEqual(fuzzy_match(program, episode), 100)

        program = {'subtitle': 'Hello World'}
        episode = {'title': 'Goodbye World'}
        self.assertNotEqual(fuzzy_match(program, episode), 100)


if __name__ == '__main__':
    unittest.main()
