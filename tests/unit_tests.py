from COVIDMonitor.main import app

def test_monitor():
	response = app.test_client().get('/monitor')

	assert response.status_code == 200
	assert response.data == b'Welcome to the Covid Monitor!'

def test_upload():
	response = app.test_client.get('/upload')
	assert response.status_code == 200

def test_query():
	response = app.test_client.get('/query')
	assert response.status_code == 200

def test_date():
	response = app.test_client.get('/data')
	assert response.status_code == 200