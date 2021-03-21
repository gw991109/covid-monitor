import csv
import json
import datetime
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

    def get_report(self, date, report):
        """
        Get a recovered/deaths/confirmed/active time series under this country
        """
        return self.reports

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
                # if country_region in sess["countries"]:
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
            dates = header[12:]
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
                        country.add_province_dated_report(province_state, date, Report(confirmed, deaths, recovered, active))
                    elif province_state != '':
                        # Adding province first then update numbers
                        country.add_province(province_state)
                        country.add_province_dated_report(province_state, date, Report(confirmed, deaths, recovered, active))
                    else:
                        # No province provided. Update country reports directly
                        country.add_province_dated_report(province_state, date, Report(confirmed, deaths, recovered, active))
                elif province_state != '':
                    # New country with states
                    country = Country(country_region)
                    country.add_province(province_state)
                    country.add_province_dated_report(province_state, date, Report(confirmed, deaths, recovered, active))
                    sess['countries'][country_region] = country
                else:
                    # Add new country with no states
                    country = Country(country_region)
                    country.add_report(date, Report(confirmed, deaths, recovered, active))
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
                print(f"Province: {province_state}. Country: {country_region}. Confirmed: {confirmed}. Deaths: {deaths}. "
                      f"Recovered: {recovered}. Active: {active}.")
                if country_region in sess["countries"]:
                # if country_region in countries_dict:
                    # Country exists, update reports
                    country = sess["countries"][country_region]
                    # country = countries_dict[country_region]
                    if province_state != '' and province_state in country.province_state:
                        # Updating province numbers for given category
                        country.add_province_dated_report(province_state, date, Report(confirmed, deaths,
                                                        recovered, active))
                    elif province_state != '':
                        # Adding province first then update numbers
                        country.add_province(province_state)
                        country.add_province_dated_report(province_state, date, Report(confirmed, deaths, recovered, active))
                    else:
                        # No province provided. Update country reports directly
                        country.add_province_dated_report(province_state, date, Report(confirmed, deaths,
                                                       recovered, active))
                elif province_state != '':
                    # Add new country with states
                    country = Country(country_region)
                    country.add_province(province_state)
                    country.add_province_dated_report(province_state, date, Report(confirmed, deaths, recovered, active))
                    sess['countries'][country_region] = country
                else:
                    # Add new country with no states
                    country = Country(country_region)
                    country.add_report(date, Report(confirmed, deaths,
                                                          recovered, active))

                    sess['countries'][country_region] = country
                    # countries_dict[country_region] = country
                    print("INSERTED")

    except EnvironmentError:
        print("With statement failed")
        return False





# return a dictionary base on the data and query
def get_result(session):
    # result = {(country, provinces):{date1: report1, date2:report2, ....}, ....}
    result = {}
    countries_query = session['query_options']['countries']
    provinces_query = session['query_options']['provinces']
    combined_keys_query = session['query_options']['combined_keys']
    print(session['query_options'])
    start_date = session['query_options']['date'][0]
    if start_date == '':
        start_date = datetime.date.min
    else:
        start_date  = get_date(start_date)
    end_date = session['query_options']['date'][0]
    if end_date == '':
        end_date = datetime.date.max
    else:
        end_date = get_data(end_date)

    for country_region in session['countries']:
        curr_country = session['countries'][country_region]

        # No provinces data
        if len(curr_country.reports) != 0:
            if (curr_country.country_region in countries_query or len(countries_query) ==0) and len(provinces_query) == 0 and (curr_country.country_region in combined_keys_query or len(combined_keys_query)==0):
                for date in curr_country.reports:
                    d = get_date(date)
                    if start_date<=d<=end_date:
                        curr_report = curr_country.reports[date]
                        if (country_region,None) in result:
                            result[(country_region,None)][date] = curr_report
                        else:
                            result[(country_region,None)] = {date: curr_report}
        # provinces are not empty, reports in Provinces object
        else:
            for province in curr_country.province_state:
                curr_combined_key = curr_country.country_region+', '+province
                if (curr_country.country_region in countries_query or len(countries_query) ==0) and (province in provinces_query or len(provinces_query) == 0) and (curr_combined_key in combined_keys_query or len(combined_keys_query)==0):
                    for date in curr_country.province_state[province].provincial_reports:
                        d = get_date(date)
                        if start_date<=d<=end_date:
                            curr_report = curr_country.province_state[province].provincial_reports[date]
                            if (country_region, province) in result:
                                result[(country_region,province)][date] = curr_report
                            else:
                                result[(country_region,province)] = {date: curr_report}
    return result

def write_to_file(result, session, filepath):
    field = session['query_options']['field']
    print(session)
    print(field)

    with open(filepath, "w") as fo:
        header = 'Country, Province, date, '+field+'\n'
        json_data={}
        json_data['reports']=[]
        if session['download_type']!= 'json':
            fo.write(header)
        for location in result:
            country = location[0]
            province = location[1]
            if province is None:
                province = ''
            for date in result[location]:
                report = result[location][date]
                data = ''
                if field == 'deaths':
                    data = report.deaths
                elif field == 'confirmed':
                    data = report.confirmed
                elif field == 'active':
                    data = report.active
                elif field == 'recovered':
                    data = report.recovered
                if data is None:
                    data = ''

                json_data['reports'].append({
                    'country': country,
                    'province': province,
                    'date': date,
                    field: data
                })
                if session['download_type']!= 'json':
                    curr_string = country+','+province+','+date+','+data+'\n'
                    fo.write(curr_string)
            if session['download_type']== 'json':
                json.dump(json_data,fo)



def change_date_format(date_string):
    date_lst = date_string.split('-')
    month = date_lst[0]
    day = date_lst[1]
    year = date_lst[2][-2:]

    if month[0] == '0':
        month = month[-1]
    if day[0] =='0':
        day = day[-1]
    print(date_lst)
    return month+'/'+day+'/'+year



def get_date(date_string):
    # date_string follow the formate mm/dd/yy
    date_lst = date_string.split('/')
    print(date_string)
    print(date_lst)
    month = int(date_lst[0])
    day = int(date_lst[1])
    year = int('20'+date_lst[2])

    return datetime.date(year, month, day)