import requests
import json
import os
from pymongo import MongoClient
import time
    
api_endpoint = "https://api.core.ac.uk/v3/"

# in case we have a mongodb database
#MONGO_DB_URL = "mongodb://mongo:27017/"
#MONGO_DB_NAME = "papers_db"
#MONGO_COLLECTION_NAME = "papers"


def query_api(url_fragment, query, api_key, is_scroll=False, limit=100, scrollId=None):
    headers={"Authorization":"Bearer "+api_key}
    query = {"q":query, "limit":limit}
    if not is_scroll:
        response = requests.post(f"{api_endpoint}{url_fragment}",data = json.dumps(query), headers=headers)
    elif not scrollId:
        query["scroll"]="true"
        response = requests.post(f"{api_endpoint}{url_fragment}",data = json.dumps(query),headers=headers)
    else:
        query["scrollId"]=scrollId
        response = requests.post(f"{api_endpoint}{url_fragment}",data = json.dumps(query),headers=headers)
    if response.status_code ==200:
        print("Rate Limit:", response.headers.get('X-RateLimit-Limit'))
        print("Rate Limit Retry After:", response.headers.get('X-RateLimit-Retry-After'))
        return response.json(), response.elapsed.total_seconds()

    else:
        print(f"Error code {response.status_code}, {response.content}")

def scroll(search_url, query, extract_info_callback=None):
    allresults = []
    count = 0
    scrollId=None
    while True:
        result, elapsed =query_api(search_url, query, is_scroll=True, scrollId=scrollId)
        scrollId=result["scrollId"]
        totalhits = result["totalHits"]
        result_size = len(result["results"])
        if result_size==0:
            break
        for hit in result["results"]:
            if extract_info_callback:
              allresults.append(extract_info_callback(hit))
            else:
              allresults.append(hit)
        count+=result_size
        print(f"{count}/{totalhits} {elapsed}s")
    return allresults

# in case we have a mongodb database
#def save_to_mongodb(data):
    #client = MongoClient(MONGO_DB_URL)
    #db = client[MONGO_DB_NAME]
    #collection = db[MONGO_COLLECTION_NAME]
    #collection.insert_many(data)

def save_json(json_object, filename): 
    with open(filename, 'w') as f:
        f.write(json.dumps(json_object, indent=2))


def main():

    # container_name = os.getenv('HOSTNAME')
    # print(f"Container name: {container_name}")
    # try:
    #     print(container_name)
    # except ValueError:
    #     print("There's no container")

    # # Extract container index from name
    # try:
    #     worker_id = int(container_name.split('_')[-1])
    #     print(worker_id)
    # except ValueError:
    #     print("Index of container couldn't be extracted.")
    #     worker_id = 0 

    # worker_id = int(os.getenv('WORKER_ID')) # in case we use docker swarm 

    # Read API keys from env_vars.txt file
    # print(f'Worker id: {worker_id}')
    # print(f"Api Keys file: {os.getenv('API_KEY_FILE')}")
    # with open(os.getenv('API_KEY_FILE')) as f:
    #     api_keys = f.readlines()

    # for i, api_key in enumerate(api_keys):
        # Define environment variables for API key
        # env_vars = {
        #     'API_KEY': api_key.strip(),
        #     'WORKER_ID': str(i + 1)
        # }

    key = str(os.getenv('API_KEY'))
    begin_year = int(os.getenv('BEGIN_YEAR', '2015'))
    end_year = int(os.getenv('END_YEAR', '2015'))

    print(f'My API key: ', key)
    
    print(f"Extracting papers from the year {begin_year} until {end_year}...")

    print("\nQuerying the API...")

    ''' 
    There are 60 seconds in a minute, so if you can make 10 requests per minute, you should wait 6 seconds between each request. 
    This would result in approximately 10 requests per minute, keeping you within your rate limit.
    '''

    scroll_id = None
    limit = int(os.getenv('CALL_LIMIT', '5'))
    for i in range(limit): # change the amount of calls to the API 
        while True:
            try:
                query = f"yearPublished>={begin_year} AND yearPublished<={end_year}"
                results, _ = query_api("search/works", query, key, is_scroll=True, limit=1000, scrollId=scroll_id)
                if 'scrollId' in results:
                    scroll_id = results['scrollId']  # save the scrollId for the next call
                
                file_path = f'/data/{key[:4]}_papers_{i}.json'
                save_json(results['results'], file_path) # save results to a new file for each page
                # save_to_mongodb(results['results'])

                break  # if the request was successful, break the loop and proceed to the next iteration
            except Exception as e:
                print(f"Error: {e}. Retrying in 10 seconds...")
                time.sleep(10)  # if an error occurred, wait for 10 seconds before retrying
        time.sleep(6)  # pause for 6 seconds before the next request


if __name__ == "__main__":
    main()