from COVIDMonitor.main import app

def test_monitor():
	response = app.test_client().get('/monitor')

	assert response.status_code == 200
	assert response.data == b'Welcome to the Covid Monitor!'