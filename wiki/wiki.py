import requests
import csv
import os
import re
import json
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter

def clean_publisher(publisher):
    '''
    Function to clean the publisher name
    
    Parameters:
    publisher (str): the name of the publisher
    
    Returns:
    cleaned_publisher (str): the cleaned name of the publisher
    '''
    # Remove "Published by:" text
    publisher = publisher.replace("Published by:", "")
    # Remove content within parentheses or square brackets
    publisher = re.sub(r'\([^)]*\)|\[[^\]]*\]', '', publisher)
    # Remove surrounding single or double quotes
    publisher = publisher.strip('"\'')
    # If publisher contains a comma or semicolon, split by comma or semicolon and take the first part
    if ',' in publisher:
        publisher = publisher.split(',')[0].strip()
    elif ';' in publisher:
        publisher = publisher.split(';')[0].strip()
    # If publisher contains a forward slash (/), split by forward slash and take the first part
    if '/' in publisher:
        publisher = publisher.split('/')[0].strip()
    # Remove periods
    publisher = publisher.replace('.', '')
    # Remove trailing numbers
    publisher = re.sub(r'\d+$', '', publisher)
    return publisher.strip()

def get_publishers_from_directory(directory):
    '''
    Function to get all publishers from a directory of JSON files

    Parameters:
    directory (str): the directory containing the JSON files
    
    Returns:
    all_publishers (set): a set of all publishers
    '''
    all_publishers = set() # we use a set to avoid duplicates
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            publishers = get_publishers(file_path)
            all_publishers.update(publishers)
    return all_publishers

def get_publishers(json_file):
    '''
    Function to get all 'clean' publishers from a JSON file
    
    Parameters:
    json_file (str): the path to the JSON file
    
    Returns:
    publishers (set): a set of all publishers
    '''
    with open(json_file, 'r') as f:
        data = json.load(f)
    publishers = set()
    for paper in data:
        publisher = str(paper.get('publisher', ''))
        cleaned_publisher = clean_publisher(publisher)
        if cleaned_publisher:  # Check if cleaned publisher is not an empty string
            publishers.add(cleaned_publisher)
    return publishers

def get_publisher_description(publisher_name, session):
    '''
    Function to get the description of a publisher from Wikidata
    
    Parameters:
    publisher_name (str): the name of the publisher
    session (requests.Session): a session object to make HTTP requests

    Returns:
    description (str): the description of the publisher

    '''
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": publisher_name
    }

    try:
        with session.get(url, params=params) as response:
            data = response.json()
            if data.get("search"):
                try:
                    description = data["search"][0]["description"]
                    return description
                except:
                    return 'No description'
            else:
                return 'No description'
    except Exception as e:
        print(f"Failed to fetch description for {publisher_name}: {e}")
        return 'No description'

def save_publisher_descriptions(publishers, output_csv):
    '''
    Function to save the descriptions of all the publishers to a CSV file

    Parameters:
    publishers (list): a list of all publishers
    output_csv (str): the path to the output CSV file

    '''
    with requests.Session() as session:
        session.mount('https://', HTTPAdapter(max_retries=3))  # Retry 3 times in case of connection errors

        with ThreadPoolExecutor() as executor:
            descriptions = list(executor.map(lambda x: (x, get_publisher_description(x, session)), publishers))

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['publisher', 'description'])
        writer.writerows(descriptions)

if __name__ == "__main__":
    publishers = get_publishers_from_directory("/data")
    output_csv = '/data/paper_publishers.csv'

    save_publisher_descriptions(publishers, output_csv)