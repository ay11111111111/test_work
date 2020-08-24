import requests, json
from datetime import datetime, timedelta
import concurrent.futures
import threading
import schedule, time

BASE_URL = 'https://api.skypicker.com/flights'
fly_from = ['ALA', 'TSE', 'ALA', 'MOW', 'ALA', 'CIT', 'TSE', 'MOW', 'TSE', 'LED']
fly_to = ['TSE', 'ALA', 'MOW', 'ALA', 'CIT', 'ALA', 'MOW', 'TSE', 'LED', 'TSE']
DAYS_IN_MONTH = 30
result = {'cheapest_flights_for_month':[]}


def get_flights(i):
    today = datetime.today()
    date = (today + timedelta(days=i)).strftime('%d/%m/%Y')
    dict_date = {'date':date, 'flights':[]}
    print('date: ' + date)
    for j in range(len(fly_from)):
        params = {
            'flyFrom': fly_from[j],
            'to': fly_to[j],
            'dateFrom': date,
            'dateTo': date,
            'partner': 'picky',
            'v': 3
        }
        response = requests.get(BASE_URL, params=params)
        flights_dict = json.loads(response.text)
        flights = flights_dict['data']
        if flights == []:
            dict_flight = {'fly_from':fly_from[j], 'fly_to':fly_to[j], 'price':None, 'booking_token':None}
        else:
            flight_min = flights[0]
            for i in range(1, len(flights)):
                if flights[i]['price'] < flight_min['price']:
                    flight_min = flights[i]
            dict_flight = {'fly_from':fly_from[j], 'fly_to':fly_to[j], 'price':flight_min['price'], 'booking_token':flight_min['booking_token']}

        dict_date['flights'].append(dict_flight)


    lock = threading.Lock()
    lock.acquire()
    try:
        result['cheapest_flights_for_month'].append(dict_date)
        print('=============================')
        print('date: ' + date)
        print('=============================')
        for flight in dict_date['flights']:
            print('{0}-{1} '.format(flight['fly_from'], flight['fly_to']), str(flight['price'])+' EUR')
    finally:
        lock.release()


def job_function():

    with concurrent.futures.ThreadPoolExecutor(max_workers=DAYS_IN_MONTH) as executor:
        for i in range(DAYS_IN_MONTH):
            executor.submit(get_flights, i)

    with open('result.json', 'w', encoding='utf-8') as f:
         json.dump(result, f)

    print('Done')


schedule.every().day.at("00:00").do(job_function)

while True:
    schedule.run_pending()
    time.sleep(60)
