import json
import glob
import os

# Path to the folders
data_folder = '/data'
output_folder = '/dfs'

# List all JSON files in the data folder
json_files = glob.glob(os.path.join(data_folder, '*.json'))

# Path to the output file in the data folder
output_file = os.path.join(output_folder, 'all_papers.json')

# Open the output file in write mode
with open(output_file, 'w') as outfile:
    # Iterate over each JSON file
    for filename in json_files:
        # Open and read the current JSON file
        with open(filename, 'r') as infile:
            # Load the list of JSON objects
            json_list = json.load(infile)
            # Iterate over each JSON object in the list
            for obj in json_list:
                # Write the JSON object to the output file, one per line
                outfile.write(json.dumps(obj) + '\n')
