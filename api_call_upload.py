import sys
import os
import logging
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from datetime import datetime
import time
from time import sleep
import requests
import json
import pytz
import re
import threading
import paho.mqtt.client as mqtt

tz = pytz.timezone('America/Los_Angeles')
events_detected = 0
# MQTT ENV
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPICS = os.getenv('MQTT_TOPICS', '')  # comma-separated
## ENVIRONMENT VARIABLES
mongodb = os.getenv('MONGODB_IP')
mongo_port = os.getenv('MONGODB_PORT')
mongodb_name = os.getenv('MONGODB_NAME')
mongo_collection = os.getenv('MONGODB_COLLECTION')
LOGS_DIR = os.getenv('LOGS_DIR', './output_logs')
OUTPUT_FILE = LOGS_DIR + "/api-call-output-" + str(int(time.time())) + ".json"
LOOP_DELAY_SECONDS = int(os.getenv('LOOP_DELAY_SECONDS', '60'))

## FUNCTIONS
def epoch_to_dates(epoch_str: str):
    dt = datetime.fromtimestamp(int(epoch_str), tz=tz)
    formatted_date = dt.strftime("%d %b %Y %H:%M:%S")
    iso_date = dt.strftime("%Y-%m-%dT%H:%M:%S.000000%z")
    return formatted_date, iso_date

## EXTRACT SELECTED FIELDS
def extract_selected_fields(event, epoch_prefix):
    formattedDate, eventDate = epoch_to_dates(epoch_prefix)
    # check if it's a tuesday between 05:00 and 13:00
    dt = datetime.strptime(formattedDate, '%d %b %Y %H:%M:%S')
    is_tuesday = dt.weekday() == 1  # 0 = Monday, 1 = Tuesday, ...
    is_between_hours = 5 <= dt.hour < 13
    if not is_tuesday and is_between_hours:
        print("Garbage Day Event")
        return None

    score = event.get("data", {}).get("score")
    label = event.get("label")

    return {
        "id": epoch_prefix,
        "epoch": int(epoch_prefix),
        "formattedDates": formattedDate,
        "eventDate": eventDate,
        "score": score,
        "label": label
    }

## FILTER DUPLICATE EVENTS
def filter_duplicate_events(events):
    seen_epochs = set()
    filtered = []

    for event in events:
        epoch_prefix = int(re.search(r'(\d+)\.', event["id"]).group(1))
        within_range = any(abs(epoch_prefix - ts) <= 20 for ts in seen_epochs)
        if not within_range:
            seen_epochs.add(epoch_prefix)
            filtered.append(extract_selected_fields(event, epoch_prefix))
        else:
            print("Duplicate event found +/- 20 seconds: ", epoch_prefix)
            continue
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(filtered, f, indent=2)
    print(f"{len(filtered)} events written to {OUTPUT_FILE}")

## MONGO FUNCTIONS
def connect_to_mongo(retries=5, delay=2):
    for attempt in range(retries):
        try:
            client = MongoClient(f'mongodb://{mongodb}:{mongo_port}/', serverSelectionTimeoutMS=5000)
            client.server_info()
            return client
        except errors.ServerSelectionTimeoutError as err:
            logging.error(f"Attempt {attempt + 1} failed: {err}")
            print(f"Connection attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            sleep(delay)
    print("Failed to connect to MongoDB after several attempts.")
    sys.exit(1)

## grab the last record from the database
def get_last_record():
    client = connect_to_mongo()
    db = client[mongodb_name]
    collection = db[mongo_collection]
    last_record = collection.find_one(sort=[('epoch', -1)])
    if last_record is None:
        return 0
    return last_record

def on_mqtt_message(client, userdata, msg):
    print(f"[MQTT] Topic: {msg.topic}, Payload: {msg.payload.decode()}")
    # Optionally: process the payload here

def start_mqtt_listener():
    if not MQTT_BROKER or not MQTT_TOPICS:
        print("MQTT_BROKER or MQTT_TOPICS not set. Skipping MQTT listener.")
        return
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_message = on_mqtt_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    for topic in [t.strip() for t in MQTT_TOPICS.split(',') if t.strip()]:
        print(f"Subscribing to MQTT topic: {topic}")
        client.subscribe(topic)
    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
    print("MQTT listener started.")

## insert json to mongo
def insert_json_to_mongo(json_file):
    client = connect_to_mongo()
    db = client[mongodb_name]
    collection = db[mongo_collection]

    # Load JSON data from file
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error reading or parsing JSON file: {e}")
        print(f"Error reading or parsing JSON file: {e}")
        sys.exit(1)
    print("Uploading data to MongoDB...")
    # Insert each object into MongoDB and confirm addition
    for item in data:
        # Check for duplicates in the collection
        existing_record = collection.find_one({'epoch': item['epoch']})
        if existing_record:
            # print(f"Record with epoch {item['epoch']} already exists. Skipping.")
            logging.info(f"Duplicate record with epoch {item['epoch']}. Skipped.")
            continue
        # Insert into MongoDB
        try:
            result = collection.insert_one(item)
            if result.acknowledged:
                print(f"Record with epoch {item['epoch']} added successfully.")
            else:
                print(f"Failed to add record with epoch {item['epoch']}.")
        except errors.PyMongoError as e:
            logging.error(f"Error inserting record with epoch {item['epoch']}: {e}")
            print(f"Error occurred while inserting record with epoch {item['epoch']}: {e}")

## FRIGATE FUNCTIONS
## make api call to frigate with the last record
def make_api_call():
    last_record = get_last_record()    
    # print(last_record.get('epoch'))
    frigate_server = os.getenv('FRIGATE_SERVER')
    events_filter = "?camera=front_yard&labels=explosion&fireworks"
    date_filter = f"&after={last_record.get('epoch')}"
    # request_url = (f"{frigate_server}{events_filter}")
    request_url = (f"{frigate_server}{events_filter}{date_filter}")
    print("Request URL: ",request_url)
    response = requests.get(request_url)
    clips = json.loads(response.text)
    # print(clips)
    return clips

def main():
    start_mqtt_listener()
    iteration = 1
    try:
        while True:
            print(f"\n--- Iteration {iteration} ---")
            events = make_api_call()
            if events:
                filter_duplicate_events(events)
                insert_json_to_mongo(OUTPUT_FILE)
            else:
                print("No events found.")
            print(f"Sleeping for {LOOP_DELAY_SECONDS} seconds...")
            sleep(LOOP_DELAY_SECONDS)
            iteration += 1
    except KeyboardInterrupt:
        print("\nGraceful shutdown: Keyboard interrupt received. Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    load_dotenv()
    main()
