from flask import Flask

app = Flask("Assignment 2")

@app.route('/monitor')
def welcome_monitor():
	return 'Welcome to the Covid Monitor!'

if __name__ == "__main__":
	app.run()