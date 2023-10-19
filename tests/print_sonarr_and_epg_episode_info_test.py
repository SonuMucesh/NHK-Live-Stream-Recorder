import unittest
from datetime import datetime
from main import print_sonarr_and_epg_episode_info


class TestMain(unittest.TestCase):
    def setUp(self):
        self.epg_program_sub_title = "EPG Title"
        self.epg_air_date = "2022-01-01"
        self.epg_converted_air_date = datetime.strptime(self.epg_air_date, '%Y-%m-%d')
        self.sonarr_episode_title = "Sonarr Title"
        self.sonarr_air_date = "2022-01-02"
        self.converted_sonarr_air_date = datetime.strptime(self.sonarr_air_date, '%Y-%m-%d')
        self.fuzzy_match_ratio = 0.8

    def test_print_sonarr_and_epg_episode_info(self):
        # This test will check the function with all parameters
        print_sonarr_and_epg_episode_info(self.epg_program_sub_title, self.epg_air_date, self.epg_converted_air_date,
                                          self.sonarr_episode_title, self.sonarr_air_date,
                                          self.converted_sonarr_air_date,
                                          self.fuzzy_match_ratio)

    def test_print_sonarr_and_epg_episode_info_no_converted_dates(self):
        # This test will check the function when the converted dates are None
        print_sonarr_and_epg_episode_info(self.epg_program_sub_title, self.epg_air_date, None,
                                          self.sonarr_episode_title, self.sonarr_air_date, None)

    def test_print_sonarr_and_epg_episode_info_no_fuzzy_match_ratio(self):
        # This test will check the function when the fuzzy match ratio is None
        print_sonarr_and_epg_episode_info(self.epg_program_sub_title, self.epg_air_date, self.epg_converted_air_date,
                                          self.sonarr_episode_title, self.sonarr_air_date,
                                          self.converted_sonarr_air_date)


if __name__ == '__main__':
    unittest.main()
