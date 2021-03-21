from typing import Any
from data_objects import *;
from flask import Flask, render_template, url_for, redirect, request, session, \
    send_file
from flask_session import Session
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


class Country:
    """
    A country class representing a country.

    --- Attributes ---
    province_state: A dictionary of provinces.
    country_region: Name of this country or region.
    time_series: Time series of this country as a whole.

    """
    province_state = None
    country_region = None
    reports = None

    def __init__(self, country_region=None):
        self.country_region = country_region
        self.province_state = {}
        self.reports = {}

    def add_report(self, date, report):
        self.reports[date] = report

    def add_dated_report(self, date, category, num):
        """
        Add a recovered/deaths/confirmed/active time series under this country
        """
        if date in self.reports:
            self.reports[date].set_data(category, num)
        else:
            report = Report()
            report.set_data(category, num)
            self.reports[date] = report

    def add_province(self, province_state):
        """
        Adding a new province for this country
        """
        self.province_state[province_state] = Province(province_state)

    def get_province(self, province_state):
        if province_state in self.province_state:
            return self.province_state[province_state]
        return None

    def add_province_dated_report(self, province_state, date, report):
        """
        Set time series for the given province.
        """
        if province_state in self.province_state:
            self.province_state[province_state].add_report(date, report)
            return True
        return False

    def get_province_dated_report(self, province_state, date):
        if province_state in self.province_state:
            if date in self.province_state[province_state].reports:
                return self.province_state[province_state].reports[date]
        return None

    def update_province_dated_report(self, province_state, date, category, num):
        if province_state in self.province_state:
            self.province_state[province_state].add_dated_report(date, category, num)
        return False

    def get_province_reports(self, province_state):
        """
        Return the type of time series from this province
        """
        if province_state in self.province_state:
            return self.province_state[province_state].get_reports()
        return None

class Province:
    """
    A class representing a province.
    ---Attributes---
    province_state: name of this province
    provincial_reports: A list of reports for this province
    """
    province_state = None
    provincial_reports = None

    def __init__(self, province_state):
        self.province_state = province_state
        self.provincial_reports = {}

    def add_report(self, date, report):
        """
        Add a recovered/deaths/confirmed/active time series under this province
        """
        self.provincial_reports[date] = report
        return True

    def add_dated_report(self, date, category, num):
        """
        Used specifically for updating one category of a report
        """
        if date in self.provincial_reports:
            report = self.provincial_reports[date]
            report.set_data(category, num)
        else:
            report = Report()
            report.set_data(category, num)
            self.provincial_reports[date] = report

    def get_reports(self):
        """
        Get a recovered/deaths/confirmed/active time series under this province
        """
        return self.provincial_reports

    def get_dated_report(self, date):
        if date in self.provincial_reports:
            return self.provincial_reports[date]


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
                return split[3] + split[4]
    return "incorrect"


def process_file(path, filename, session):
    file_type = determine_file_type(path, filename)
    print(f"File type: {file_type}")
    if file_type == "incorrect":
        return False
    session['file_type'] = file_type
    if file_type == "world":
        date = filename[:-4]
        date = change_date_format(date)
        return process_daily_report_world(path, date, session)

    if file_type == "us":
        date = filename[:-4]
        date = change_date_format(date)
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


def process_global_timeseries(path, category, sess):
    try:
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)
            dates = header[4:]
            for line in csv_reader:
                province_state = line[0]
                country_region = line[1]
                print(country_region)
                if country_region in sess["countries"]:
                    # Country exists, update reports
                    country = sess["countries"][country_region]
                    if province_state != '' and province_state in country.province_state:
                        # Updating province numbers for given category
                        for index in range(len(dates)):
                            date = dates[index]
                            num = line[index+4]
                            country.update_province_dated_report(province_state, date, category, num)
                    elif province_state != '':
                        # Adding province first then update numbers
                        country.add_province(province_state)
                        for index in range(len(dates)):
                            date = dates[index]
                            num = line[index+4]
                            country.update_province_dated_report(province_state, date, category, num)
                    else:
                        # No province provided. Update country reports directly
                        for index in range(len(dates)):
                            date = dates[index]
                            num = line[index+4]
                            country.add_dated_report(date, category, num)
                elif province_state != '':
                    # Add country and add provinces and updated reports.
                    country = Country(country_region)
                    country.add_province(province_state)
                    for index in range(len(dates)):
                        date = dates[index]
                        num = line[index+4]
                        report = Report()
                        report.set_data(category, num)
                        country.add_province_dated_report(province_state, date, report)
                    sess['countries'][country_region] = country
                else:
                    # Country does not exist in our records, add country then update reports
                    country = Country(country_region)
                    for index in range(len(dates)):
                        date = dates[index]
                        num = line[index+4]
                        country.add_dated_report(date, category, num)
                    sess['countries'][country_region] = country

        return True
    except EnvironmentError:
        print("With statement failed")
        return False


def process_us_timeseries(path, category, sess):
    try:
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)
            if category == "deaths":
                dates = header[12:]
            else:
                dates = header[11:]
            for line in csv_reader:
                province_state = line[6]
                country_region = line[7]
                print(f"Country: {country_region}. Province: {province_state}.")
                if country_region in sess["countries"]:
                    # Country exists, update reports
                    country = sess["countries"][country_region]
                    if province_state != '' and province_state in country.province_state:
                        # Updating province numbers for given category
                        for index in range(len(dates)):
                            date = dates[index]
                            num = line[index + 10]
                            country.update_province_dated_report(province_state, date, category, num)
                    elif province_state != '':
                        # Adding province first then update numbers
                        country.add_province(province_state)
                        for index in range(len(dates)):
                            date = dates[index]
                            num = line[index + 10]
                            country.update_province_dated_report(province_state, date, category, num)
                    else:
                        # No province provided. Update country reports directly
                        for index in range(len(dates)):
                            date = dates[index]
                            num = line[index + 10]
                            country.add_dated_report(date, category, num)
                elif province_state != '':
                    # Add country and add provinces and updated reports.
                    country = Country(country_region)
                    country.add_province(province_state)
                    for index in range(len(dates)):
                        date = dates[index]
                        num = line[index + 10]
                        report = Report()
                        report.set_data(category, num)
                        country.add_province_dated_report(province_state, date, report)
                    sess['countries'][country_region] = country
                else:
                    # Country does not exist in records and no province provided, add country then update reports
                    country = Country(country_region)
                    for index in range(len(dates)):
                        date = dates[index]
                        num = line[index + 10]
                        country.add_dated_report(date, category, num)
                    sess['countries'][country_region] = country
        return True
    except EnvironmentError:
        print("With statement failed")
        return False


def process_daily_report_world(path, date, sess):
    try:
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for line in csv_reader:
                province_state = line[2]
                country_region = line[3]
                confirmed = line[7]
                deaths = line[8]
                recovered = line[9]
                active = line[10]
                if country_region in sess["countries"]:
                    # Country exists, update reports
                    country = sess["countries"][country_region]
                    if province_state != '' and province_state in country.province_state:
                        # Updating province numbers for given category
                        country.add_province_dated_report(province_state, date,
                                                          Report(confirmed,
                                                                 deaths,
                                                                 recovered,
                                                                 active))
                    elif province_state != '':
                        # Adding province first then update numbers
                        country.add_province(province_state)
                        country.add_province_dated_report(province_state, date,
                                                          Report(confirmed,
                                                                 deaths,
                                                                 recovered,
                                                                 active))
                    else:
                        # No province provided. Update country reports directly
                        country.add_province_dated_report(province_state, date,
                                                          Report(confirmed,
                                                                 deaths,
                                                                 recovered,
                                                                 active))
                elif province_state != '':
                    # New country with states
                    country = Country(country_region)
                    country.add_province(province_state)
                    country.add_province_dated_report(province_state, date,
                                                      Report(confirmed, deaths,
                                                             recovered, active))
                    sess['countries'][country_region] = country
                else:
                    # Add new country with no states
                    country = Country(country_region)
                    country.add_report(date, Report(confirmed, deaths,
                                                    recovered, active))
                    sess['countries'][country_region] = country
        return True
    except EnvironmentError:
        print("With statement failed")
        return False


def process_daily_report_us(path, date, sess):
    try:
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for line in csv_reader:
                province_state = line[0]
                country_region = line[1]
                confirmed = line[5]
                deaths = line[6]
                recovered = line[7]
                active = line[8]
                print(
                    f"Province: {province_state}. Country: {country_region}. Confirmed: {confirmed}. Deaths: {deaths}. "
                    f"Recovered: {recovered}. Active: {active}.")
                if country_region in sess["countries"]:
                    # Country exists, update reports
                    country = sess["countries"][country_region]
                    if province_state != '' and province_state in country.province_state:
                        # Updating province numbers for given category
                        country.add_province_dated_report(province_state, date,
                                                          Report(confirmed,
                                                                 deaths,
                                                                 recovered,
                                                                 active))
                    elif province_state != '':
                        # Adding province first then update numbers
                        country.add_province(province_state)
                        country.add_province_dated_report(province_state, date,
                                                          Report(confirmed,
                                                                 deaths,
                                                                 recovered,
                                                                 active))
                    else:
                        # No province provided. Update country reports directly
                        country.add_province_dated_report(province_state, date,
                                                          Report(confirmed,
                                                                 deaths,
                                                                 recovered,
                                                                 active))
                elif province_state != '':
                    # Add new country with states
                    country = Country(country_region)
                    country.add_province(province_state)
                    country.add_province_dated_report(province_state, date,
                                                      Report(confirmed, deaths,
                                                             recovered, active))
                    sess['countries'][country_region] = country
                else:
                    # Add new country with no states
                    country = Country(country_region)
                    country.add_report(date, Report(confirmed, deaths,
                                                    recovered, active))

                    sess['countries'][country_region] = country
    except EnvironmentError:
        print("With statement failed")
        return False


@app.route('/')
def home():
    session['query_options'] = {'countries': [], 'provinces': [],
                                'combined_keys': [], 'date': ['',''], 'field': 'deaths'}
    session['all_world_reports'] = {}
    session['all_us_reports'] = {}
    session['countries'] = {}
    session['download_type'] = ''
    session['download_file'] = ''
    session['file_type'] = ''
    session['report_type'] = ''
    session['uploaded'] = False
    return redirect(url_for("upload"))

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
            session['uploaded'] = True

        except():
            print('error')
            info = 'failure'
            session['uploaded'] = False

    return render_template("upload.html", text=info)


@app.route('/query', methods = ['POST', 'GET'])
def query():
	message = ''
	if request.method == 'POST':
		if request.form['btn'] == 'add_country' and request.form['country'] != '':
			session['query_options']['countries'].append(request.form['country'])
		elif request.form['btn'] == 'add_provinces' and request.form['provinces'] != '':
			session['query_options']['provinces'].append(request.form['provinces'])
		elif request.form['btn'] == 'add_combined_key' and request.form['combined_key'] != '':
			session['query_options']['combined_keys'].append(request.form['combined_key'])
		elif request.form['btn'] == 'reset':
			session['query_options']['countries'] = []
			session['query_options']['provinces'] = []
			session['query_options']['combined_keys'] = []
			session['query_options']['date'] = ['','']
		elif  request.form['btn'] == 'add_date':
			if request.form['date'] != '' and request.form['start'] == '' and request.form['end']=='':
				date_string = request.form['date']
				session['query_options']['date'] = [date_string,date_string]
			elif request.form['start'] != '' and request.form['end'] != '' and request.form['date'] == '':
				start_string = request.form['start']
				end_string = request.form['end']
				session['query_options']['date'] = [start_string, end_string]
			else:
				session['query_options']['date'] = ['','']
				message = 'invalid date'


	if session['query_options']['date'][0] == session['query_options']['date'][1]:
		message = session['query_options']['date'][0]
	elif len(session['query_options']['date']) == 2:
		message = session['query_options']['date'][0] + ' to ' + session['query_options']['date'][1]

	return render_template('query.html', countries=session['query_options']['countries'],
	provinces=session['query_options']['provinces'], combined_keys=session['query_options']['combined_keys'],
	date = message)



@app.route('/data', methods=['POST', 'GET'])
def data():
    session['query_options']['field']=request.args.get('field')
    return render_template('data.html')


@app.route('/download_file')
def download_file():
    filename = 'result.'
    p = './instance/downloads/'
    vailid = True
    session['download_type'] = request.args.get('file_type')
    if session['download_type'] == 'json':
        print("json")
        filename = filename + 'json'
    elif session['download_type'] == 'csv':
        print('csv')
        filename = filename + 'csv'
    elif session['download_type'] == 'txt':
        print('text')
        filename = filename + 'txt'
    else:
        vailid = False
        print("invalid file type")
    if vailid:
        print(session['query_options'])
        result = get_result(session)

        write_to_file(result, session, p+filename)
        session['download_file'] = p+filename
        print(p+filename)
        try:
            return send_file(session['download_file'], as_attachment=True)
        except:
            return "Error, file not found!"
    return "Error, file not found!"


if __name__ == "__main__":
    app.run(debug = True)

