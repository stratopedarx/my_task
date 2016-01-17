import re
import exceptions
import datetime
from lxml import html
import requests
"""
proxies = {"http": "http://localhost:8888",
           "https": "http://localhost:8888",}
"""
def build_search_request(from_place, to_place, departure_date, arrival_date=False):
    """
    MAIN function build search requsts and print information abot flights
    """
    #Check input parametrs and build search request
    check_param(from_place, to_place, departure_date, arrival_date)

    print "Please wait..."
    try:
        #take name departion and destnation from IATA-CODE
        departure = name_from_iata_code(from_place)
        destination = name_from_iata_code(to_place)
    except IndexError:
        raise exceptions.IndexError("websiteError")

    #get request for url with sid
    url = "http://www.flyniki.com/en-RU/booking/flight/vacancy.php"
    values = {'departure': from_place,
              'destination': to_place,
              'outboundDate': departure_date,
              'returnDate': '',
              'oneway': 1,
              'openDateOverview': 0,
              'adultCount': 1,
              'childCount': 0,
              'infantCount': 0,}
    if arrival_date is not False:
        values['oneway'] = 'on'
        values['returnDate'] = arrival_date

    #session with cookies
    session = requests.Session()
    body_sid = session.get(url, params=values)

    #post request and take body html
    url_sid = body_sid.url
    payload = [('_ajax[templates][]', 'main'),
                ('_ajax[templates][]', 'priceoverview'),
                ('_ajax[templates][]', 'infos'),
                ('_ajax[templates][]', 'flightinfo'),
                ('_ajax[requestParams][departure]', departure),
                ('_ajax[requestParams][destination]', destination),
                ('_ajax[requestParams][returnDeparture]', ''),
                ('_ajax[requestParams][returnDestination]', ''),
                ('_ajax[requestParams][outboundDate]', departure_date),
                ('_ajax[requestParams][returnDate]', departure_date),
                ('_ajax[requestParams][adultCount]', 1),
                ('_ajax[requestParams][childCount]', 0),
                ('_ajax[requestParams][infantCount]', 0),
                ('_ajax[requestParams][openDateOverview]', ''),
                ('_ajax[requestParams][oneway]', 'on')]
    if arrival_date is not False:
        payload[-1] = ('_ajax[requestParams][oneway]', '')
        payload[9] = ('_ajax[requestParams][returnDate]', arrival_date)

    headers = {'Referer': url_sid,
               'X-Requested-With': 'XMLHttpRequest',
               'Accept': 'application/json, text/javascript, */*'}

    body = session.post(url_sid, data=payload, headers=headers)   #proxies=proxies
    body_parse = body.json()["templates"]["main"]
    parser = html.fromstring(body_parse)

    #parse_xpath return dict with information about flights
    outbound = parse_xpath(parser, ".//*[@id='flighttables']/div[1]/div/table/tbody/tr[position() mod 2 = 1]")
    return_flight = parse_xpath(parser, ".//*[@id='flighttables']/div[3]/div/table/tbody/tr[position() mod 2 = 1]")

    #take the currency
    currency = parser.xpath(".//*[@id='flighttables']/div/div/table/thead/tr/th[5]/text()")[0]

    #print result
    print "OUTBOUND FLIGHT %s" % departure_date
    for i in outbound:
        len_price = len(outbound[i]["price"])
        if len_price == 3:
            print ("From %s to %s ->>Start/end %s-%s ->>Duration of journey: %s ->>Price: 1. %s%s/ 2. %s%s/ 3. %s%s"
                % (departure, destination, outbound[i]["time"][0],outbound[i]["time"][1], outbound[i]["time_of_path"][0],
                   outbound[i]["price"][0].rstrip('.0'), currency, outbound[i]["price"][1].rstrip('.0'),
                   currency, outbound[i]["price"][2].rstrip('.0'), currency))
        elif len_price == 2:
            print ("From %s to %s ->>Start/end %s-%s ->>Duration of journey: %s ->>Price: 1. %s%s/ 2. %s%s"
                   % (departure, destination, outbound[i]["time"][0],outbound[i]["time"][1], outbound[i]["time_of_path"][0],
                      outbound[i]["price"][0].rstrip('.0'), currency, outbound[i]["price"][1].rstrip('.0'), currency))
        elif len_price == 1:
            print ("From %s to %s ->>Start/end %s-%s ->>Duration of journey: %s ->>Price: 1. %s%s"
                   % (departure, destination, outbound[i]["time"][0],outbound[i]["time"][1],
                      outbound[i]["time_of_path"][0],outbound[i]["price"][0].rstrip('.0'), currency))

    if arrival_date is not False:
        #print result return_flight
        print "RETURN FLIGHT %s" % arrival_date
        for i in return_flight:
            len_price = len(return_flight[i]["price"])
            if len_price == 3:
                print ("From %s to %s ->>Start/end %s - %s ->>Duration of journey: %s ->>Price: 1. %s%s/ 2. %s%s/ 3. %s%s"
                    % (departure, destination, return_flight[i]["time"][0],return_flight[i]["time"][1], return_flight[i]["time_of_path"][0],
                       return_flight[i]["price"][0].rstrip('.0'), currency, return_flight[i]["price"][1].rstrip('.0'),
                       currency, return_flight[i]["price"][2].rstrip('.0'), currency))
            elif len_price == 2:
                print ("From %s to %s ->>Start/end %s-%s ->>Duration of journey: %s ->>Price: 1. %s%s/ 2. %s%s"
                       % (departure, destination, return_flight[i]["time"][0],return_flight[i]["time"][1], return_flight[i]["time_of_path"][0],
                          return_flight[i]["price"][0].rstrip('.0'), currency, return_flight[i]["price"][1].rstrip('.0'), currency))
            elif len_price == 1:
                print ("From %s to %s ->>Start/end %s-%s ->> Duration of journey: %s ->>Price: 1. %s%s"
                       % (departure, destination, return_flight[i]["time"][0],return_flight[i]["time"][1],
                          return_flight[i]["time_of_path"][0],return_flight[i]["price"][0].rstrip('.0'), currency))


#use xPath to retrieve the desired information
def parse_xpath(xml, url):
    result = {}
    i=1
    #take odd with fligts from outbound flights
    flights = xml.xpath(url)
    for flight in flights:
        if flight.xpath('.//div[@class="current"]/span/text()') == [] : continue
        information = {}
        information["time"] = flight.xpath('.//td[@class="table-text-left"]/span/time/text()')    #return list [time-time]
        information["time_of_path"] = flight.xpath('.//td[@class="table-text-left"][2]/span/text()')
        information["price"] = flight.xpath('.//div[@class="lowest"]/span/text()')
        result[i] = information
        i += 1
    return result


def name_from_iata_code(iata_code):
    url_home = "http://www.flyniki.com"
    url = '/en-RU/offers/search/api/limit/5/departure/'
    return requests.get(url_home+url+iata_code).json()['results'][0]['departurename']

def check_param(from_place, to_place, departure_date, arrival_date):
    """
    Check input param and raise Exception
    """
    if re.match('([a-zA-Z][a-zA-Z][a-zA-Z])', from_place) is None or len(from_place) != 3:
            raise exceptions.ValueError('Invalid IATA from_place code')
    if re.match('([a-zA-Z][a-zA-Z][a-zA-Z])', to_place) is None or len(to_place) != 3:
        raise exceptions.ValueError('Invalid IATA to_place code')
    try:
        dep_date = datetime.date(int(departure_date[:4]), int(departure_date[5:7]), int(departure_date[8:10]))
    except ValueError:
        raise exceptions.ValueError('Invalid departure_date')
    if arrival_date is not False:
        try:
            arr_date = datetime.date(int(arrival_date[:4]), int(arrival_date[5:7]), int(arrival_date[8:10]))
        except ValueError:
            raise exceptions.ValueError('Invalid arrival_date')
        if dep_date > arr_date:
            raise exceptions.ValueError('arrival_date can not be earlier departure_date')


#call MAIN function
from_place = raw_input("Where are you coming from, enter please IATA-code:")
to_place = raw_input("where are you flying, enter please IATA-code:")
departure_date = raw_input("When? Enter please in format 2015-12-25:")
answer = raw_input("Will you fly back? yes or no:")
if answer.lower() == 'yes':
	arrival_date = raw_input("When? Enter please in format 2015-12-29:")
else:
	arrival_date = False

"""
from_place = 'DME'
to_place = 'BER'
departure_date = '2015-12-30'
arrival_date = '2016-01-12'
"""

build_search_request(from_place, to_place, departure_date, arrival_date)