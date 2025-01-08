import os
import json
import urllib.request
import boto3
from datetime import datetime, timezone


def format_game_data(game):
    """
    Format match data to include Home Team, Away Team, Time, and Venue.
    """
    home_team = game.get("HomeTeamName", "Unknown")
    away_team = game.get("AwayTeamName", "Unknown")
    time = game.get("DateTime", "Unknown")
    venue = game.get("VenueId", "Unknown")  # Adjust field based on actual API response.

    return (
        f"Home Team: {home_team}\n"
        f"Away Team: {away_team}\n"
        f"Time: {time}\n"
        f"Venue: {venue}\n"
    )


def lambda_handler(event, context):
    # Get environment variables
    api_key = os.getenv("SOCCER_API_KEY")
    sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
    area = os.getenv("AREA", "Europe")  # Default to Europe if AREA is not set.
    sns_client = boto3.client("sns")
    
    # Fetch current date
    utc_now = datetime.now(timezone.utc)
    today_date = utc_now.strftime("%Y-%m-%d")
    
    print(f"Fetching matches for date: {today_date}")
    
    # Fetch data from the API
    api_url = f"https://api.sportsdata.io/v3/soccer/scores/json/GamesByDate/{today_date}?area={area}&key={api_key}"
    print(api_url)
    
    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
            
            # Format match details
            messages = [format_game_data(match) for match in data]
            final_message = "\n---\n".join(messages) if messages else "No matches available for today."
            
            print("Match Details:")
            print(final_message)
            
            # Publish to SNS
            try:
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=final_message,
                    Subject="Soccer Match Updates"
                )
                print("Message published to SNS successfully.")
            except Exception as sns_error:
                print(f"Error publishing to SNS: {sns_error}")
                return {"statusCode": 500, "body": "Error publishing to SNS"}
    
    except Exception as api_error:
        print(f"Error fetching data from API: {api_error}")
        return {"statusCode": 500, "body": "Error fetching data"}
    
    return {"statusCode": 200, "body": "Data processed and sent to SNS"}
