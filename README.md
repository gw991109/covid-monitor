# Assignment 2 COVIDMonitor

### Prerequisites

You must have Python-3 and a package manager [pip] installed on your computer 

Additionally you will need to install the following packages: 

```bash
pip install flask
pip install flask_session
pip install pytest
pip install pytest-cov
```

### Running The Code

You can start by running main.py, which is in the folder COVIDMonitor. main.py has the main method that will start the program. 


```bash
python main.py
```

If you want to try another data file or different query, you have to clear your browser history first to prevent download the previous result file.

## Running Tests 

A starter template for unit tests can be found under tests/unit_tests.py

To run unit tests with coverage, run the following command:

```bash
pytest --cov-report term --cov=COVIDMonitor tests/unit_tests.py
```

## Pair Programming

### Features were pair programmed
- upload page and uploading file feature
- query page and process the user's query options
#### upload page
- Driver: Gerald Wu
- Navigator: Pao Hua Lin
- Reflection: While we were clear on the idea of how this page would look like, there was a lot of assistance that I needed throughout the writing of this function since I am not familiar with flask at all and wasn't sure on how to write up the page formatting. I needed my partner to look up some code examples throughout the session which was very time consuming and inefficient.
#### query page
- Driver: Gerald Wu
- Navigator: Pao Hua Lin
- Reflection: Since is our first time using flask, we spend lot of time to find out how to get and store the informations from user input. It is very efficent using pair programming when coding this part, one person can search for the solution and other person can work on the code. 

## Program design
Base on the data files, we decided to have a class Country that has attributes country_region, province_state, and reports. country_region is a string that represent the name on the country. If the data file does not contain the information about province/state, then the attribute province_state will be an empty dictionary, and the report(deaths, confirmed, active, recovered) will be store in the reports dictionary with the key is the date. If the data file contain the information about province/state, then reports dictionary will be empty, province_state will be a dictionary that the key is the date and value is a Province object, the reports will be store in Province object.
We also has a class Report for storing the report information, the attributes are deaths, active, confirmed, and recovered.
This design has the benefit that it is very well structured. Queries can only be made to look up either country, province, or combined key, and since we have the classes country and province already stored in dictionaries with keys as the country and province names, we can directly look for these country and province instances which store their individual reports.
And since combined key is just a combination of country and province, we can just break up the string and query like normal.
Reports each represent the confirmed, deaths, recovered, and active cases for a certain day, therefore each country or province instance has a reports attribute which is a dictionary with dates as keys and reports for that day's report. While this means there needs to be many report instances, and may be inefficient with respect to time, it is very structured and organized. 

