import unittest
from main import *

path = 'C:\\Users\\Gerald\\Desktop\\UofT\\Y3\\CSC301\\A2\\csvs\\'


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = {}

    def setUp(self):
        self.session['query_options'] = {'countries': [], 'provinces': [],
                                    'combined_keys': [], 'date': ['', ''],
                                    'field': 'deaths'}
        self.session['all_world_reports'] = {}
        self.session['all_us_reports'] = {}
        self.session['countries'] = {}
        self.session['download_type'] = ''
        self.session['download_file'] = ''
        self.session['file_type'] = ''
        self.session['report_type'] = ''
        self.session['uploaded'] = False

    def tearDown(self):
        self.session = {}

    def test_determine_file_type(self):
        self.assertEqual(determine_file_type(path + 'time_series_covid19_confirmed_global.csv', 'time_series_covid19_confirmed_global.csv'), 'confirmedglobal')
        self.assertEqual(determine_file_type(path + 'time_series_covid19_deaths_global.csv', 'time_series_covid19_deaths_global.csv'), 'deathsglobal')
        self.assertEqual(determine_file_type(path + 'time_series_covid19_recovered_global.csv', 'time_series_covid19_recovered_global.csv'), 'recoveredglobal')
        self.assertEqual(determine_file_type(path + 'time_series_covid19_confirmed_US.csv', 'time_series_covid19_confirmed_US.csv'), 'confirmedUS')
        self.assertEqual(determine_file_type(path + 'time_series_covid19_deaths_US.csv', 'time_series_covid19_deaths_US.csv'), 'deathsUS')
        self.assertEqual(determine_file_type(path + '01-02-2021.csv', '01-02-2021.csv'), 'us')
        self.assertEqual(determine_file_type(path + '12-01-2020.csv', '12-01-2020.csv'), 'world')
        self.assertEqual(determine_file_type(path + 'incorrect.txt', 'incorrect.txt'), 'incorrect')

    def test_process_file(self):
        self.assertEqual(process_file(
            path + 'time_series_covid19_confirmed_global.csv',
            'time_series_covid19_confirmed_global.csv', self.session), True)
        self.assertEqual(
            process_file(path + 'time_series_covid19_deaths_global.csv',
                                'time_series_covid19_deaths_global.csv', True),
            'deathsglobal')
        self.assertEqual(process_file(
            path + 'time_series_covid19_recovered_global.csv',
            'time_series_covid19_recovered_global.csv', self.session), True)
        self.assertEqual(
            process_file(path + 'time_series_covid19_confirmed_US.csv',
                                'time_series_covid19_confirmed_US.csv', self.session),
            True)
        self.assertEqual(
            process_file(path + 'time_series_covid19_deaths_US.csv',
                                'time_series_covid19_deaths_US.csv', self.session),
            True)
        self.assertEqual(
            process_file(path + '01-02-2021.csv', '01-02-2021.csv', self.session),
            True)
        self.assertEqual(
            process_file(path + '12-01-2020.csv', '12-01-2020.csv', self.session),
            True)
        self.assertEqual(
            process_file(path + 'incorrect.txt', 'incorrect.txt', self.session),
            False)

    def test_process_global_timeseries(self):
        process_global_timeseries(
            path + 'time_series_covid19_confirmed_global.csv',
            'confirmed', session)
        country = self.session['countries']['Canada']
        report = country.get_province_dated_report('Saskatchewan', '3/18/21')
        self.assertEqual(report.get_confirmed(), 31085)

        process_global_timeseries(
            path + 'time_series_covid19_deaaths_global.csv',
            'deaths', self.session)
        self.assertEqual(report.get_deaths(), 414)

        process_global_timeseries(
            path + 'time_series_covid19_recovered_global.csv',
            'recovered', self.session)
        recovered = country.get_report('3/18/21')
        self.assertEqual(recovered.get_recovered(), 873615)


if __name__ == '__main__':
    unittest.main()
