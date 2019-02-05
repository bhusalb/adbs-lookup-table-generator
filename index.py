from ratelimit import limits, sleep_and_retry

import requests
import arrow
from bs4 import BeautifulSoup

FIFTEEN_MINUTES = 900

MONTH_NAMES = ['बैशाख', 'जेष्ठ', 'आषाढ', 'श्रावण', 'भाद्र', 'आश्विन', 'कार्तिक', 'मंसिर', 'पौष', 'माघ', 'फाल्गुन',
               'चैत्र']

DAY_NAMES = ['सोमवार', 'मगलवार', 'बुधवार', 'बिहिवार', 'शुक्रवार', 'शनिवार', 'आइतवार']

NEPALI_NUMS = {
    '०': '0',
    '१': '1',
    '२': '2',
    '३': '3',
    '४': '4',
    '५': '5',
    '६': '6',
    '७': '7',
    '८': '8',
    '९': '9'
}


@sleep_and_retry
@limits(calls=1, period=8)
def call_api(date):
    print(date)
    response = requests.post('https://www.ashesh.com.np/nepali-date-converter.php', date)

    # if response.status_code != '200':
    #     raise Exception('API response: {}'.format(response.status_code))
    return response


start_date = arrow.get('1995-01-01')
end_date = arrow.get('2010-01-01')

loop_date = start_date
while loop_date < end_date:

    try:
        res = call_api({
            'yeare': loop_date.year,
            'month': loop_date.format('MMMM'),
            'day': loop_date.day
        })

        page = BeautifulSoup(res.content, features="html.parser")

        date_div = page.select('.unicode_wrap .inner')[1]

        print(date_div.text[5:10], date_div.text.split(' '))
        parts = date_div.text.split(' ')
        year = parts[0][5:]
        month = parts[1]
        day = parts[2]

        en_year = ''.join(list(map(lambda c: NEPALI_NUMS[c], year)))
        en_month = str(MONTH_NAMES.index(month) + 1)
        en_day = ''.join(list(map(lambda c: NEPALI_NUMS[c], day)))

        complete_date = '-'.join([en_year, en_month.rjust(2, '0'), en_day.rjust(2, '0')])

    except:
        complete_date = ''

    with open('dates.csv', 'a') as datefile:
        datefile.write(','.join([loop_date.format('YYYY-MM-DD'), complete_date]) + '\n')
    loop_date = loop_date.shift(days=1)
