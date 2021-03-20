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


uploads_dir = os.path.join(app.instance_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)


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

