from flask import Flask, render_template, url_for, redirect, request, flash, session, send_file
from flask_session import Session
import os

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)


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
	incident_rate = None
	case_fatality_ratio = None
	fips = None
	admin2 = None

	def __init__(self, province_state = None,
	country_region = None,
	last_update = None,
	lat = None,
	long = None,
	confirmed = None,
	deaths = None,
	recovered = None,
	active = None,
	incident_rate = None,
	case_fatality_ratio = None,
	fips = None,
	admin2 = None):
		self.province_state = province_state
		self.country_region = country_region
		self.last_update = last_update
		self.lat = lat
		self.long = long
		self.confirmed = confirmed
		self.deaths = deaths
		self.recovered = recovered
		self.active = active
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
	province_state = None,
	country_region = None,
	last_update = None,
	lat = None,
	long = None,
	confirmed = None,
	deaths = None,
	recovered = None,
	active = None,
	incident_rate = None,
	case_fatality_ratio = None,
	fips = None,
	admin2 = None,
	total_test_results=None,
	people_hospitalized = None,
	iso3 = None,
	testing_rate = None,
	hospitalization_rate = None):
		super().__init__(province_state,
			country_region,
			last_update,
			lat,
			long,
			confirmed,
			deaths,
			recovered,
			active,
			incident_rate,
			case_fatality_ratio,
			fips,
			admin2)
		self.uid = uid
		self.total_test_results = total_test_results
		self.people_hospitalized = people_hospitalized
		self.iso3 = iso3
		self.testing_rate = testing_rate
		self.hospitalization_rate = hospitalization_rate


class Country:
	province_state = None
	country_region = None
	lat = None
	long = None
	time_series = None
	def __init__(self, time_series, province_state = None, country_region = None,
				 lat = None, long = None):
		self.province_state = province_state
		self.country_region = country_region
		self.lat = lat
		self.long = long
		self.time_series = time_series


@app.route('/')
def home():
	session['query_options'] = {'countries':[], 'provinces':[], 'combined_keys':[], 'date':['']}
	return redirect(url_for("welcome_monitor"))

@app.route('/monitor')
def welcome_monitor():
	return render_template("index.html")

uploads_dir = os.path.join(app.instance_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

@app.route('/upload', methods=["GET", "POST"])
def upload():
	if request.method == "POST" and request.files:
		file = request.files["file"]
		file.save(os.path.join(uploads_dir, file.filename))
		print("file saved")
		return redirect(request.url)
	return render_template("upload.html")


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
			session['query_options']['date'] = []
		elif  request.form['btn'] == 'add_date':
			if request.form['date'] != '' and request.form['start'] == '' and request.form['end']=='':
				session['query_options']['date'] = [request.form['date']]
			elif request.form['start'] != '' and request.form['end'] != '' and request.form['date'] == '':
				session['query_options']['date'] = [request.form['start'], request.form['end']]
			else:
				session['query_options']['date'] = []
				message = 'invalid date'

	if len(session['query_options']['date']) == 1:
		message = session['query_options']['date'][0]
	elif len(session['query_options']['date']) == 2:
		message = session['query_options']['date'][0] + ' to ' + session['query_options']['date'][1]
	return render_template('query.html', countries=session['query_options']['countries'],
	provinces=session['query_options']['provinces'], combined_keys=session['query_options']['combined_keys'],
	date = message)


if __name__ == "__main__":
	app.run()
