import requests
import boto3
import json
import os
from datetime import datetime,timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix","Accra"]

# Initialize AWS S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def fetch_weather_data(city):
    """Fetch weather data from OpenWeather API for a given city."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=imperial"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "conditions": data["weather"][0]["description"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    else:
        print(f"Failed to fetch weather data for {city}. HTTP Status Code: {response.status_code}")
        return None

def upload_to_s3(data, bucket_name, file_name):
    """Upload data to AWS S3 as a JSON file."""
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        return True
    except Exception as e:
        print(f"Failed to upload {file_name} to S3: {e}")
        return False

if __name__ == "__main__":
    for city in CITIES:
        print(f"Processing weather data for {city}")
        weather_data = fetch_weather_data(city)
        if weather_data:
            file_name = f"weather-data/{city.replace(' ', '-')}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
            if upload_to_s3(weather_data, S3_BUCKET_NAME, file_name):
                print(f"Saved weather data to: {file_name}")
                print(f"Successfully processed {city}\n")
            else:
                print(f"Failed to process {city}\n")
        else:
            print(f"Failed to fetch data for {city}\n")