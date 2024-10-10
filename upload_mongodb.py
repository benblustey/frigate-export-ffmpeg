import sys
import json
import logging
from pymongo import MongoClient, errors
from time import sleep

# Set up logging
logging.basicConfig(filename='mongo_insert.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def connect_to_mongo(retries=5, delay=2):
    for attempt in range(retries):
        try:
            client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
            client.server_info()
            return client
        except errors.ServerSelectionTimeoutError as err:
            logging.error(f"Attempt {attempt + 1} failed: {err}")
            print(f"Connection attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            sleep(delay)
    print("Failed to connect to MongoDB after several attempts.")
    sys.exit(1)

def insert_json_to_mongo(json_file):
    client = connect_to_mongo()
    db = client['fw_db']
    collection = db['events']

    # Load JSON data from file
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error reading or parsing JSON file: {e}")
        print(f"Error reading or parsing JSON file: {e}")
        sys.exit(1)

    # Insert each object into MongoDB and confirm addition
    for item in data:
        # Validate the presence of the 'epoch' key
        if 'epoch' not in item:
            print(f"Skipping item {item}, missing 'epoch' key.")
            logging.error(f"Item {item} missing 'epoch' key. Skipped.")
            continue

        # Check for duplicates in the collection
        existing_record = collection.find_one({'epoch': item['epoch']})
        if existing_record:
            print(f"Record with epoch {item['epoch']} already exists. Skipping.")
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

if __name__ == "__main__":
    # Check if a JSON file was passed as an argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    insert_json_to_mongo(json_file)
