import requests
from bs4 import BeautifulSoup
import re
import csv
import time
from datetime import datetime
import logging
import sys
import os

# Set up logging with log rotation
from logging.handlers import RotatingFileHandler

log_file = 'weather_scraper.log'
max_log_size = 5 * 1024 * 1024  # 5 MB
log_backup_count = 3

handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=log_backup_count)
logging.basicConfig(handlers=[handler], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_weather_data():
    url = "https://weather.com/en-IN/weather/today/l/25.60,85.15"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data: {e}")
        return None

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

def write_to_csv(data, filename):
    try:
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Date', 'Current Time', 'Current Temperature', 'Day and Night Temperatures', 
                                 'Feels Like Temperature', 'High/Low', 'Wind', 'Humidity', 'Dew Point', 
                                 'Pressure', 'UV Index', 'Visibility', 'Moon Phase', 'Chance of Rain', 
                                 'Weather Condition'])
            writer.writerow(data)
    except IOError as e:
        logging.error(f"Failed to write to CSV: {e}")

def get_current_csv_filename():
    return f'weather_data_{datetime.now().strftime("%Y%m")}.csv'

def main():
    logging.info("Weather data collection started")

    while True:
        try:
            data = fetch_weather_data()
            if data is None:
                time.sleep(60)  # Wait for 1 minute before retrying
                continue

            current_date = datetime.now().strftime("%Y-%m-%d")
            data.insert(0, current_date)
            
            current_csv = get_current_csv_filename()
            write_to_csv(data, current_csv)

            logging.info(f"Data collected successfully and written to {current_csv}")

            time.sleep(300)  # Sleep for 5 minutes
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            time.sleep(60)  # Wait for 1 minute before retrying

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Exiting.")
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
    finally:
        logging.info("Program finished.")