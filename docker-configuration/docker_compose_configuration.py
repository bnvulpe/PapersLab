import os

"""
This is a script that takes a template of a docker compose and configures it with the environment variables
dynamically. We assign each API key to a different worker.
"""
def load_env_file(file_path):
    """
    Load environment variables from a .env file.
    
    Args:
        file_path (str): Path to the .env file.
    """
    with open(file_path, 'r') as f:
        for line in f:
            # Skip empty lines and lines starting with '#'
            if line.strip() and not line.startswith('#'):
                # Split the line into key-value pairs
                key, value = line.strip().split('=', 1)
                # Set the environment variable
                os.environ[key] = value



def configure_docker_compose(template_file, output_file, api_keys_file, output_folder):
    load_env_file('.env')

    # Read the template file and the API keys file
    with open(template_file, 'r') as template:
        template_content = template.readlines()

    with open(api_keys_file, 'r') as keys:
        api_keys = keys.readlines()
    
    num_workers = len(api_keys)  # Number of workers is dictated by the number of API keys
    
    # Extracting environment variables from .env file
    begin_year = int(os.getenv('BEGIN_YEAR'))
    original_end_year = int(os.getenv('END_YEAR'))
    limit = int(os.getenv('CALL_LIMIT'))

    # Calculate the time range for each worker
    time_range = (original_end_year - begin_year) / num_workers

    # Find the start and end indices of the worker block
    start_index = template_content.index('  worker:\n')
    end_index = template_content.index('  # Other services defined here\n')

    for i, key in enumerate(api_keys, start=1):
        

        # Calculate the time range for the current worker
        worker_begin_year = round(float(begin_year + (i - 1) * time_range))
        worker_end_year = round(float(begin_year + i * time_range))

        new_worker = template_content[start_index:end_index].copy()  # Copy the worker lines

        print(new_worker)

        # Modify relevant lines
        new_worker[0] = f'  worker_{i}:\n'
        for j, line in enumerate(new_worker):
            if "- BEGIN_YEAR=" in line:
                new_worker[j] = line.replace("{BEGIN_YEAR}", str(worker_begin_year))
            elif "- END_YEAR=" in line:
                new_worker[j] = line.replace("{END_YEAR}", str(worker_end_year))
            elif "- API_KEY=" in line:
                new_worker[j] = line.replace("{API_KEY}", key.strip())
            elif "- WORKER_ID=" in line:
                new_worker[j] = line.replace("{WORKER_ID}", str(i))
            elif "- CALL_LIMIT=" in line:   
                new_worker[j] = line.replace("{CALL_LIMIT}", str(limit))
                
        #new_worker = [line for line in new_worker if "- WORKER_ID={WORKER_ID}" not in line and "- END_YEAR={END_YEAR}" not in line] # Avoid duplication
        new_worker.append('\n')
        print('\n')
        print(new_worker)
        worker_service = ''.join(new_worker)
        
        template_content.extend(worker_service)

    del template_content[start_index:end_index]# Delete the worker template
    # Save the output file with the replaced variables in the specified folder

    print(template_content)
    with open(os.path.join(output_folder, output_file), 'w') as output:
        output.writelines(template_content)

if __name__ == "__main__":
    configure_docker_compose('docker-compose.yml.template', 'docker-compose.yml', 'env_vars.txt', '/app')

