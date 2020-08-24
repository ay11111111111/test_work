import requests, json
from datetime import datetime, timedelta
import threading, time
import concurrent.futures

CHECK_URL = 'https://booking-api.skypicker.com/api/v0.1/check_flights'
DAYS_IN_MONTH = 30


def send_get_request(booking_token):
    params = {
        'v': 2,
        'booking_token': booking_token,
        'bnum': 1,
        'pnum': 1,
        'affily': 'picky_{market}'
    }
    response = requests.get(CHECK_URL, params=params)
    flights_changes = json.loads(response.text)

    return flights_changes


def check_flights(i):
    date = i['date']
    for flight in i['flights']:
        if flight['booking_token']!=None:
            flights_changes = send_get_request(flight['booking_token'])

            while flights_changes['flights_checked']!=True:
                time.sleep(60)
                flights_changes = send_get_request(flight['booking_token'])

            lock = threading.Lock()
            lock.acquire()
            try:
                print('================')
                print('date: ' + date, '{0}-{1}'.format(flight['fly_from'], flight['fly_to']))
                print('flights_checked: '+ str(flights_changes['flights_checked']))
                print('flights_invalid: '+ str(flights_changes['flights_invalid']))
                print('price change:    ' + str(flights_changes['price_change']))
            finally:
                lock.release()

with concurrent.futures.ThreadPoolExecutor(max_workers=DAYS_IN_MONTH) as executor:
    with open('result.json') as f:
        data = json.load(f)
    for i in data['cheapest_flights_for_month']:
        executor.submit(check_flights, i)

print('Done checking.')
