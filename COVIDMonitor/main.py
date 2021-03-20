from flask import Flask, render_template, url_for, redirect, request, flash, \
    session, send_file
from flask_session import Session
import csv
import os

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

class Report:
    confirmed = None
    deaths = None
    recovered = None
    active = None

    def __init__(self, confirmed = None, deaths = None,
                 recovered = None, active = None, category = None, num = None):
        self.confirmed = confirmed
        self.deaths = deaths
        self.recovered = recovered
        self.active = active
        if category:
            self.set_data(category, num)

    def set_data(self, category, num):
        if category == "confirmed" or category == "Confirmed":
            self.confirmed = num
            return True
        if category == "deaths" or category == "Deaths":
            self.deaths = num
            return True
        if category == "recovered" or category == "Recovered":
            self.recovered = num
            return True
        if category == "Active" or category == "Active":
            self.active = num
            return True
        return False

    def get_confirmed(self):
        return self.confirmed

    def get_deaths(self):
        return self.deaths

    def get_recovered(self):
        return self.recovered

    def get_active(self):
        return self.active

class WorldDailyReport:
    province_state = None
    country_region = None
    last_update = None
    lat = None
    long = None
    confirmed = None
    deaths = None
    recovered = None
    active = None
    combined_key = None
    incident_rate = None
    case_fatality_ratio = None
    fips = None
    admin2 = None

    def __init__(self, province_state=None,
                 country_region=None,
                 last_update=None,
                 lat=None,
                 long=None,
                 confirmed=None,
                 deaths=None,
                 recovered=None,
                 active=None,
                 combined_key=None,
                 incident_rate=None,
                 case_fatality_ratio=None,
                 fips=None,
                 admin2=None):
        self.province_state = province_state
        self.country_region = country_region
        self.last_update = last_update
        self.lat = lat
        self.long = long
        self.confirmed = confirmed
        self.deaths = deaths
        self.recovered = recovered
        self.active = active
        self.combined_key = combined_key
        self.incident_rate = incident_rate
        self.case_fatality_ratio = case_fatality_ratio
        self.fips = fips
        self.admin2 = admin2


class USDailyReport(WorldDailyReport):
    total_test_results = None
    people_hospitalized = None
    uid = None
    iso3 = None
    testing_rate = None
    hospitalization_rate = None

    def __init__(self, uid,
                 province_state=None,
                 country_region=None,
                 last_update=None,
                 lat=None,
                 long=None,
                 confirmed=None,
                 deaths=None,
                 recovered=None,
                 active=None,
                 incident_rate=None,
                 case_fatality_ratio=None,
                 fips=None,
                 total_test_results=None,
                 people_hospitalized=None,
                 iso3=None,
                 testing_rate=None,
                 hospitalization_rate=None):
        super().__init__(province_state,
                         country_region,
                         last_update,
                         lat,
                         long,
                         confirmed,
                         deaths,
                         recovered,
                         active,
                         None,
                         incident_rate,
                         case_fatality_ratio,
                         fips)
        self.uid = uid
        self.total_test_results = total_test_results
        self.people_hospitalized = people_hospitalized
        self.iso3 = iso3
        self.testing_rate = testing_rate
        self.hospitalization_rate = hospitalization_rate

class Country:
    province_state = None
    country_region = None
    reports = None

    def __init__(self, country_region=None):
        self.country_region = country_region
        self.province_state = {}
        self.reports = {}

    def add_dated_report(self, date, report):
        self.reports[date] = report

    def get_reports(self):
        return self.reports

    def add_province(self, province_state):
        self.province_state[province_state] = Province(province_state)

    def get_province(self, province_state):
        if province_state in self.province_state:
            return self.province_state[province_state]
        return None

    def add_province_dated_report(self, province_state, date, report):
        if province_state in self.province_state:
            self.province_state[province_state].add_report(date, report)
        return None

    def get_province_dated_report(self, province_state, date):
        if province_state in self.province_state:
            if date in self.province_state[province_state].reports:
                return self.province_state[province_state].reports[date]
        return None

    def get_province_reports(self, province_state):
        if province_state in self.province_state:
            return self.province_state[province_state].get_reports()
        return None

class Province:
    province_state = None
    provincial_reports = None

    def __init__(self, province_state):
        self.province_state = province_state
        self.provincial_reports = {}

    def add_report(self, date, report):
        self.provincial_reports[date] = report

    def add_dated_report(self, date, num, category):
        if date in self.provincial_reports:
            report = self.provincial_reports[date]
            report.set_data(category, num)
        else:
            report = Report()
            report.set_data(category, num)
            self.provincial_reports[date] = report

    def get_reports(self):
        return self.provincial_reports

    def get_dated_report(self, date):
        if date in self.provincial_reports:
            return self.provincial_reports[date]


class Date:
    date = None
    reports = {}

    def __init__(self, date):
        self.date = date

    def add_report(self, country, report):
        self.reports[country] = report

def determine_file_type(path, filename):
    if ".csv" in filename:
        filename = filename[:-4]
        print(f"Truncated file name: {filename}")
        try:
            datetime.datetime.strptime(filename, '%m-%d-%Y')
            # daily report format, find out if its world or US
            with open(path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                entry = next(csv_reader)[0]
                if entry == 'FIPS':
                    return "world"
                elif entry == "Province_State":
                    return "us"
        except ValueError:
            # check if it's a time series
            split = filename.split('_')
            if len(split) == 5:
                return split[4] + split[5]
    return "incorrect"

def process_file(path, filename, session):
    file_type = determine_file_type(path, filename)
    print(f"File type: {file_type}")
    if file_type == "incorrect":
        return False
    if file_type == "world":
        date = filename[:-4]
        return process_daily_report_world(path, date, session)

    if file_type == "us":
        date = filename[:-4]
        return process_daily_report_us(path, date, session)

    if file_type == "deathsglobal":
        process_global_timeseries(path, "deaths", session)
        return True
    if file_type == "deathsUS":
        process_us_timeseries(path, "deaths", session)
        return True
    if file_type == "confirmedglobal":
        process_global_timeseries(path, "confirmed", session)
        return True
    if file_type == "confirmedUS":
        process_us_timeseries(path, "confirmed", session)
        return True
    if file_type == "recoveredglobal":
        process_global_timeseries(path, "recovered", session)
        return True
    return False


def process_daily_report_world(path, date, session):
    date_object = Date(date)
    with open(path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for line in csv_reader:
            fips = line[0]
            admin2 = line[1]
            province_state = line[2]
            country_region = line[3]
            last_update = line[4]
            lat = line[5]
            long = line[6]
            confirmed = line[7]
            deaths = line[8]
            recovered = line[9]
            active = line[10]
            combined_key = line[11]
            incident_rate = line[12]
            fatality_ratio = line[13]
            report = WorldDailyReport(province_state, country_region,
                                      last_update, lat, long, confirmed, deaths,
                                      recovered, active, combined_key,
                                      incident_rate, fatality_ratio, fips,
                                      admin2)
            date_object.add_report(country_region, report)
    session['all_world_reports'][date] = date_object


def process_daily_report_us(path, date, session):
    with open(path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for line in csv_reader:
            province_state = line[0]
            country_region = line[1]
            last_update = line[2]
            lat = line[3]
            long = line[4]
            confirmed = line[5]
            deaths = line[6]
            recovered = line[7]
            active = line[8]
            fips = line[9]
            incident_rate = line[10]
            total_test_results = line[11]
            people_hospitalized = line[12]
            fatality_ratio = line[13]
            uid = line[14]
            iso3 = line[15]
            testing_rate = line[16]
            hospitlization_rate = line[17]
            report = USDailyReport(uid, province_state, country_region,
                                   last_update, lat, long, confirmed, deaths,
                                   recovered, active, incident_rate,
                                   fatality_ratio, fips, total_test_results,
                                   people_hospitalized, iso3, testing_rate,
                                   hospitlization_rate)
            session['all_us_reports'][date] = report


@app.route('/')
def home():
    session['query_options'] = {'countries': [], 'provinces': [],
                                'combined_keys': [], 'date': ['']}
    return redirect(url_for("welcome_monitor"))


@app.route('/monitor')
def welcome_monitor():
    return render_template("index.html")


uploads_dir = os.path.join(app.instance_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)


@app.route('/upload', methods=["GET", "POST"])
def upload():
    info = ''
    if request.method == "POST" and request.files:
        try:
            file = request.files["file"]
            path = os.path.join(uploads_dir, file.filename)
            file.save(path)
            print(f"Path: {path}")
            print(f"File name: {file.filename}")
            process_file(path, file.filename, session)
            print("file saved")
            info = 'success'

        except():
            print('error')
            info = 'failure'

    return render_template("upload.html", text=info)


@app.route('/query', methods=['POST', 'GET'])
def query():
    message = ''
    if request.method == 'POST':
        if request.form['btn'] == 'add_country' and request.form[
            'country'] != '':
            session['query_options']['countries'].append(
                request.form['country'])
        elif request.form['btn'] == 'add_provinces' and request.form[
            'provinces'] != '':
            session['query_options']['provinces'].append(
                request.form['provinces'])
        elif request.form['btn'] == 'add_combined_key' and request.form[
            'combined_key'] != '':
            session['query_options']['combined_keys'].append(
                request.form['combined_key'])
        elif request.form['btn'] == 'reset':
            session['query_options']['countries'] = []
            session['query_options']['provinces'] = []
            session['query_options']['combined_keys'] = []
            session['query_options']['date'] = []
        elif request.form['btn'] == 'add_date':
            if request.form['date'] != '' and request.form['start'] == '' and \
                    request.form['end'] == '':
                session['query_options']['date'] = [request.form['date']]
            elif request.form['start'] != '' and request.form['end'] != '' and \
                    request.form['date'] == '':
                session['query_options']['date'] = [request.form['start'],
                                                    request.form['end']]
            else:
                session['query_options']['date'] = []
                message = 'invalid date'

    if len(session['query_options']['date']) == 1:
        message = session['query_options']['date'][0]
    elif len(session['query_options']['date']) == 2:
        message = session['query_options']['date'][0] + ' to ' + \
                  session['query_options']['date'][1]
    return render_template('query.html',
                           countries=session['query_options']['countries'],
                           provinces=session['query_options']['provinces'],
                           combined_keys=session['query_options'][
                               'combined_keys'],
                           date=message)


if __name__ == "__main__":
    app.run()
