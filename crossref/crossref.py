import requests
import csv
import os
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def formatterParams(title, authors):
    '''
    Function to clean the title and authors name of the paper
    
    Parameters:
    title (str): the title of the paper
    authors (str): the name of the author
    
    Returns:
    title (str): the cleaned title of the paper
    authors (str): the cleaned name the name of the author
    '''
    if authors:
        authors_str = authors[0]['name']
    else:
        authors_str = ''
    return title, authors_str

def find_publisher_location(json_data):
    '''
    Function to find the publisher location in the JSON response

    Parameters:
    json_data (dict): the JSON response from the API

    Returns:
    str: the publisher location if found, otherwise None
    '''
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == "publisher-location":
                return value
            elif isinstance(value, (dict, list)):
                result = find_publisher_location(value)
                if result:
                    return result
    elif isinstance(json_data, list):
        for item in json_data:
            result = find_publisher_location(item)
            if result:
                return result
    return None

def create_or_append_csv(filename, fieldnames, data):
    '''
    Function to create a new CSV file or append data to an existing CSV file

    Parameters:
    filename (str): the name of the CSV file
    fieldnames (list): the field names for the CSV file
    data (dict): the data to be written to the CSV file
    '''
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

def process_paper(paper):
    '''
    Function to process each paper asynchronously

    Parameters:
    paper (dict): paper information from JSON data
    '''
    title = paper['title']
    authors = paper['authors']
    title, authors = formatterParams(title, authors)
    url = f"https://api.crossref.org/works?query.author={authors}&query.title={title}"
    
    with requests.Session() as session:
        response = session.get(url, stream=True)
        if response.status_code == 200:
            data = response.json()
            publisher_location = find_publisher_location(data)
            if publisher_location:
                # Añadir los datos del título del artículo y la ubicación del editor a la lista
                # print(f'Title: {paper["title"]}, Location: {publisher_location}')
                return ({'original_title': paper['title'], 'publisher_location': publisher_location})
            else:
                # Añadir "No location found" a la lista si no se encuentra la ubicación del editor
                # print(f'Title: {paper["title"]}, Location: "No location found"')
                return ({'original_title': paper['title'], 'publisher_location': 'No location found'})
        else:
            print("Failed to fetch data from the API")


def returnLocationFolder(directory, output_csv):
    '''
    Function to return the publisher location of the papers in the JSON data

    Parameters:
    directory (str): the directory containing the JSON files
    output_csv (str): the name of the CSV file to write the data
    '''
    papers = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as json_file:
                data_list = json.load(json_file)
                papers.extend(data_list)
    
    # Parallelize the processing of papers
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_paper, papers)

    df = pd.DataFrame(results)
    return df

if __name__ == "__main__":
    directory = "/data"
    output_csv = '/data/paper_locations.csv'

    df_data = returnLocationFolder(directory, output_csv)
    df_data.to_csv(output_csv, index=False)
