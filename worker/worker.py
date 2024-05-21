import requests
import json
import os
import time
import socket
    
api_endpoint = "https://api.core.ac.uk/v3/"

def query_api(url_fragment, query, api_key, is_scroll=False, limit=100, scrollId=None):
    ''' 
    Function to query the API and return the results

    Parameters:
    url_fragment (str): the url fragment to be appended to the base url
    query (str): the query to be passed to the API
    api_key (str): the API key to be used for authentication
    is_scroll (bool): whether the query is a scroll query or not
    limit (int): the number of results to be returned
    scrollId (str): the scrollId to be used for the next scroll query

    Returns:
    response.json() (dict): the response from the API in JSON format
    response.elapsed.total_seconds() (float): the time taken for the request to complete

    '''
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
    '''
    Function to scroll through the results of a query
    
    Parameters:
    search_url (str): the url fragment to be appended to the base url
    query (str): the query to be passed to the API
    extract_info_callback (function): a callback function to extract information from the results
    
    Returns:
    allresults (list): a list of all the results from the query
    '''

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

def save_json(json_object, filename): 
    '''
    Function to save a JSON object to a file. Used for saving the results of the API query. 
    Since we are calling the API multiple times (CALL_LIMIT), we save the results to a new file for each page of results.

    Parameters:
    json_object (dict): the JSON object to be saved
    filename (str): the name of the file to save the JSON object to

    '''
    with open(filename, 'w') as f:
        f.write(json.dumps(json_object, indent=2))
def main():
    '''
    Main function to extract papers from the API.
    
    The function extracts papers from the API based on the year range and call_limit provided in the environment variables and saves the results to a file in the /data directory.
    
    '''

    worker_id = int(os.getenv('WORKER_ID')) # in case there's an intended use of docker swarm or any other orchestration tool, used for identificaction
    key = str(os.getenv('API_KEY'))
    begin_year = int(os.getenv('BEGIN_YEAR', '2015'))
    end_year = int(os.getenv('END_YEAR', '2015'))

    print(f'Hi! My ID is: ', worker_id, '\n')
    
    print(f"I'm extracting papers from the year {begin_year} until {end_year}...\n")

    print("\nQuerying the API...")

    ''' 
    There's an API rate limit of 10 request/minute. Since there are 60 seconds in a minute, this script should wait 6 seconds between each request. 
    This would result in approximately 10 requests per minute, keeping the script within the rate limit.
    '''

    scroll_id = None
    limit = int(os.getenv('CALL_LIMIT', '5'))
    for i in range(limit): # amount of calls to the API per worker mentioned in the environment variable CALL_LIMIT
        while True:
            try:
                query = f"yearPublished>={begin_year} AND yearPublished<={end_year}"
                results, _ = query_api("search/works", query, key, is_scroll=True, limit=50, scrollId=scroll_id)
                if 'scrollId' in results:
                    scroll_id = results['scrollId']  # save the scrollId for the next call
                
                file_path = f'/data/{key[:4]}_papers_{i}.json'
                save_json(results['results'], file_path) # save results to a new file for each page

                break  # if the request was successful, break the loop and proceed to the next iteration
            except Exception as e:
                print(f"Error: {e}. Retrying in 10 seconds...")
                time.sleep(10)  # if an error occurred, wait for 10 seconds before retrying

        time.sleep(6)  # pause for 6 seconds before the next request


def send_message_to_coordinator(message):
    host = 'coordinator'  # Number of the container of the coordinator 
    port = 12345  # Port of the coordinator

    # Create socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Conect to the coordinator server
        client_socket.connect((host, port))

        # Send message
        client_socket.sendall(message.encode())

        print(f"Message sent to coordinator: {message}")

    except Exception as e:
        print(f"Error has occurred while sending message: {e}")
    finally:
        # Close socket
        client_socket.close()

if __name__ == "__main__":
    main()
    time.sleep(10)
    worker_id = int(os.getenv('WORKER_ID'))
    message = f"Finished extraction from worker with id {worker_id}"
    send_message_to_coordinator(message)
