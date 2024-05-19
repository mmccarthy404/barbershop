from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime

def handler(event, context):
    year = event['year']
    month = event['month']
    day = event['day']
    location = event['location']
    service = event['service']
    provider = event['provider']
    business = event['business']

    url = (f'https://go.booker.com/location/{business}/service/{location}/'
           f'{service}/availability/{year}-{month}-{day}/provider/{provider}/'
           f'no-availability-provider-date')

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')   # Headless
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Overcome limits
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    driver.implicitly_wait(10)

    if driver.find_elements(By.CLASS_NAME, 'suggested-date-links'):
        date_string = driver.find_element(By.CLASS_NAME,
                                          'suggested-date-links') \
                            .find_element(By.TAG_NAME, 'a').text
        # Add year since we don't get this from string, this may be incorrect
        # if next available date is in the new year, but this is OK since we
        # null the date if the month is incorrect and next available date will
        # never be more than 60 days out.
        date_string_w_year = f'{date_string} {year}'
        date = datetime.strptime(date_string_w_year, '%A, %B %d %Y').date()
        if date.month != datetime.strptime(month, '%m').month:
            date = None  # We're only interested in a date in selected month

    elif driver.find_elements(By.CLASS_NAME, 'next-available-top'):
        date = None

    else:
        date = datetime.strptime(f'{year} {month} {day}', '%Y %m %d').date()

    driver.quit()

    if date:
        date_str = date.strftime('%Y-%m-%d')
    else:
        date_str = None

    response = {
        'statusCode': 200,
        'headers': {},
        'body': {
            'date': date_str
        }
    }

    return response
