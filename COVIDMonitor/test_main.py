import unittest
from main import *

path = 'C:\\Users\\Gerald\\Desktop\\UofT\\Y3\\csc301\\a2\\csvs\\'


class TestMain(unittest.TestCase):

    def test_determine_file_type(self):
        self.assertEqual(determine_file_type(path + 'time_series_covid19_confirmed_global', 'time_series_covid19_confirmed_global'), 'confirmedglobal')
        self.assertEqual(determine_file_type(path + 'time_series_covid19_deaths_global', 'time_series_covid19_deaths_global'), 'deathsglobal')
        self.assertEqual(determine_file_type(path + 'time_series_covid19_recovered_global', 'time_series_covid19_recovered_global'), 'recoveredglobal')
        self.assertEqual(determine_file_type(path + 'time_series_covid19_confirmed_US', 'time_series_covid19_confirmed_US'), 'confirmedUS')
        self.assertEqual(determine_file_type(path + 'time_series_covid19_deaths_US', 'time_series_covid19_deaths_US'), 'deathsUS')
        self.assertEqual(determine_file_type(path + '01-01-2021', '01-01-2021'), 'us')
        self.assertEqual(determine_file_type(path + '12-01-2020', '12-01-2020'), 'world')


if __name__ == '__main__':
    unittest.main()
