from flask import Flask, render_template, url_for, redirect, request
# from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)

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


if __name__ == "__main__":
	app.run()
