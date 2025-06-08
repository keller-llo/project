import requests
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather_by_city(self, city):
        try:
            logger.debug(f"Fetching weather for city: {city}")
            logger.debug(f"Using API key: {self.api_key}")

            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',  # 使用摄氏度
                'lang': 'zh_cn'    # 使用中文描述
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"API Response: {data}")

            return {
                'weather': {
                    'temperature': data['main']['temp'],
                    'condition': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed']
                }
            }
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            return {'error': str(e)}

