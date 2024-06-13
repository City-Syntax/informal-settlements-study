import requests
from bs4 import BeautifulSoup
import re
import csv
import time

def fetch_weather_data():
    url = "https://weather.com/en-IN/weather/today/l/25.60,85.15"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting data
    current_time = soup.select_one('span[class^="CurrentConditions--timestamp"]').get_text(strip=True).replace('As of ', '')
    current_temp = soup.select_one('span[data-testid="TemperatureValue"][class^="CurrentConditions--tempValue"]').get_text(strip=True)
    day_night_temp = soup.select_one('div[class^="CurrentConditions--tempHiLoValue"]').get_text(separator=' ', strip=True)
    feels_like_temp = soup.select_one('span[data-testid="TemperatureValue"][class^="TodayDetailsCard--feelsLikeTempValue"]').get_text(strip=True)
    details = soup.select_one('div[class^="TodayDetailsCard--detailsContainer"]')
    high_low = details.find('div', string='High/Low').find_next_sibling('div').get_text(strip=True)
    wind = details.find('div', string='Wind').find_next_sibling('div').get_text(strip=True).replace('Wind Direction', '')
    humidity = details.find('div', string='Humidity').find_next_sibling('div').get_text(strip=True)
    dew_point = details.find('div', string='Dew Point').find_next_sibling('div').get_text(strip=True)
    pressure_raw = details.find('div', string='Pressure').find_next_sibling('div').get_text(strip=True)
    pressure_match = re.search(r'\d+\.?\d*', pressure_raw)
    pressure = pressure_match.group() + ' mb' if pressure_match else 'N/A'
    uv_index = details.find('div', string='UV Index').find_next_sibling('div').get_text(strip=True)
    visibility = details.find('div', string='Visibility').find_next_sibling('div').get_text(strip=True)
    moon_phase = details.find('div', string='Moon Phase').find_next_sibling('div').get_text(strip=True)
    hourly_weather = soup.select_one('div[class^="HourlyWeatherCard--TableWrapper"]')
    first_hour = hourly_weather.select_one('li')
    chance_of_rain = re.search(r'\d+', first_hour.select_one('span[class^="Column--precip"]').get_text(strip=True)).group() + "%"
    weather_condition = first_hour.select_one('svg[set="weather"]').find('title').get_text(strip=True)

    return [current_time, current_temp, day_night_temp, feels_like_temp, high_low, wind, humidity, dew_point,
            pressure, uv_index, visibility, moon_phase, chance_of_rain, weather_condition]

def write_to_csv(data):
    with open('weather_data.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def main():
    header = ['Current Time', 'Current Temperature', 'Day and Night Temperatures', 'Feels Like Temperature',
              'High/Low', 'Wind', 'Humidity', 'Dew Point', 'Pressure', 'UV Index', 'Visibility', 'Moon Phase',
              'Chance of Rain', 'Weather Condition']
    with open('weather_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
    
    while True:
        data = fetch_weather_data()
        write_to_csv(data)
        time.sleep(300)  # 600 seconds -> 10 minutes

if __name__ == "__main__":
    main()