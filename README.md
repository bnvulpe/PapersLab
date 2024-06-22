# PapersLab: Extraction, Processing and Analysis of Public Papers

## About

The project aims to offer a convenient data structure on scientific papers and their specific characteristics, providing an efficient structure for both data processing and subsequent storage and analysis, according to the client's needs.

#### Objectives

- **Scientific Data Collection**: Obtain detailed and updated scientific article data from various API sources.
- **Information Enrichment**: Add relevant metadata to scientific articles, improving the quality and usefulness of the dataset.
- **Efficient Storage**: Use specialized databases to optimally store and manage data.
- **Analysis Facilitation**: Provide tools and environments that facilitate advanced data analysis by researchers and data scientists.

## Infraestructure

###General outline of the Infrastructure
![infrastructure_schema](https://github.com/bnvulpe/PapersLab/assets/77082096/c8ca5219-ba71-428f-9958-e1bc3b08df18)

This section identifies and describes the key components of the infrastructure, including the container services to be used.

### Microservices

The infrastructure is based on microservices designed for the efficient extraction of data from scientific papers using multiple API keys. An additional service was implemented to merge the data extracted by each worker, so that we end the extraction stage with a single JSON file containing all the information.

In addition, a Docker volume is implemented to store the downloaded data, which facilitates its subsequent storage, processing and manipulation in the following stages of the project (in different data storage and processing services such as Neo4j and Elasticsearch). The reason behind the choice of these services is based on the following points:

- **Neo4j:** is a graph database that is ideal for modeling and representing complex relationships between entities, such as authors of papers, citations between papers, and connections between scientific concepts. By taking advantage of Neo4j's ability to store data in the form of graphs, they can easily model relationships between attributes. This enables efficient queries to discover patterns and relationships between data.

- **Elasticsearch:** search engine that can be used to index and search the contents of scientific papers, as well as to store and query the information obtained. Elasticsearch offers advanced full-text search, aggregation, data analysis and visualization capabilities, making it easy to extract meaningful information from large unstructured datasets. In addition, Elasticsearch is highly scalable and fault-tolerant, making it suitable for handling large data volumes and distributed workloads.

- **MySQL:** is a widely-used relational database management system (RDBMS) that stores and manages the structured data of scientific papers, enabling fast querying of temporal and thematic data. Its high performance, scalability, and ease of use make it ideal for handling large datasets and supporting concurrent access by multiple users in a distributed environment.

### Folder contents:

- **coordinator:**
  - *coordinator.py:* script that implements a TCP server that waits to receive messages from the workers' containers and once it has received as many messages as workers it activates port 1234 to start the 'merge' service process.
  - *Dockerfile:* Dockerfile that builds the image in charge of executing the script *coordinator.py*.
    
- **databases:**
  - *docker-compose.yml* builds three services: Neo4j, MySQL and Elasticsearch. Neo4j is configured in single mode, with authentication, plugins, and ports exposed for interaction. MySQL is configured with user credentials, a specific database, and exposes the standard MySQL port.
  - *initbd/init.sql* loads data from CSV files into three separate temporary tables. Then, using insert queries, it transfers that data to a main table called papers, updating existing records if necessary. Finally, it deletes the temporary tables and verifies that the data has been correctly inserted into the papers table.
  - *init.txt* file given to import the nodes and relationships to Neo4j.

- **dfs:**
  - *graph.ipynb:* script to process the data using PySpark. It performs operations to join, transform, and generate relationships between document and author data, and then saves this information to CSV files for further analysis. The script loads data from CSV and JSON files, joins them according to unique identifiers, creates relationships between documents and authors, and extracts individual nodes for documents and authors. 
  - *crossref_service.ipynb:* script that takes information from a paper in JSON format, extracts the name of the publisher and performs a Crossref API search to get its location. It then appends this data, including the original paper title and publisher location, to a CSV file. This process is performed asynchronously to handle multiple papers efficiently. In addition, it takes advantage of the concurrent.futures.ThreadPoolExecutor module to process the papers concurrently. Because of the runtime it is not executed in the final workflow.
  - *wiki-publishers.ipynb:* script in charge of cleaning the authors from the JSON files extracted by the workers, accessing the Wiki API and saving the information obtained in a CSV file.
  - *init_elasticdb.ipynb:* takes care of connecting to Elasticsearch, creating an index if it doesn't exist and then loading data from a JSON file into Elasticsearch. Once the data is loaded, it performs a simple search query to verify successful load.
  - *renaming.ipynb:* renames CSV files based on their current locations and the new names provided.
  - *run_notebooks.sh:* runs several Jupyter notebooks in parallel. It then runs the "text_classification.ipynb", "time_data.ipynb" and "wiki-publishers.ipynb" notebooks in the background using jupyter nbconvert. Then waits for all background processes to finish and run the additional notebooks, "graph.ipynb" and "renaming.ipynb".
  - *text_classification.ipynb:* The script uses PySpark to read data from JSON files, then calls a Hugging Face API to classify the content of each document. The classification is based on the document title and uses a specific Hugging Face model. The classification result is printed and then saved to a new CSV file containing the document ID and the topic assigned by the model.
  - *time_data.ipynb:* uses PySpark to read JSON data and extract the month and day of the week from the document publication dates. It then saves this information to a CSV file.
    
- **docker-configuration:**
  - *docker-compose.yml.template:* Docker Compose Template used to generate the configuration file.
  - *docker_compose_configuration.py:* Python script that generates the desired Docker Compose from the template, creating and assigning workers with the corresponding API keys, along with other automated assignments.
  - *Dockerfile:* File to build the Docker image needed to run *docker_compose_configuration.py*.
  - *docker-compose.yml:* Docker Compose used to mount the above image and create the volume where the data will be stored.
  - *.env:* File to store environment variables such as BEGIN_YEAR, END_YEAR and CALL_LIMIT, customizable by user.
  - *env_vars.txt:* Text file containing the API keys (one on each line), ensuring a worker for each key. Said API keys can be obtained from the [CORE API webpage](https://core.ac.uk/services/api#what-is-included).

- **merger:**
  - *Dockerfile:* script that prepares an environment to run the Python application, ensuring that the necessary dependencies and utilities are available.
  - *merge.py:* combines multiple JSON files into a single output JSON file.

- **spark:**
  - *.env* environment variable that will determine the number of spark nodes that the cluster will have.
  - *build.sh* prepares a Dockerized environment to run a Spark cluster with JupyterLab support.
  - *cluster-base.Dockerfile* creates a Docker image based on a light version of Debian with Java Runtime Environment (JRE).
  - *docker-compose.yml* Sets up a cluster environment with JupyterLab, Spark Master and Spark Worker services. Defines a shared volume called shared-workspace to store persistent data and share files between services.

- **worker:**
  - *worker.py:* script in charge of data extraction from the API.
  - *requirements.txt:* specifies the libraries needed to run the script.
  - *Dockerfile:* builds the image responsible for running *worker.py* and installs the libraries specified in requirements.txt.

### Workflow steps

- **1.1 Data extraction (Worker):** 
  - *Contribution to efficient data handling:* The use of multiple workers distributes the workload and speeds up the data extraction process by parallelizing API requests. This optimizes performance and ensures fast and effective extraction of large volumes of data.
  - *Integration with other components:* Data extracted by each worker is stored in a shared Docker volume, allowing uniform access to data from other components of the system, such as Elasticsearch, MySQL and Neo4j databases.

- **1.2 Coordinator:**  This microservice acts as an orchestrator, ensuring that services are executed in the proper order and providing a signal to enable the execution of subsequent services once the workers have completed their task.

- **1.3 Data Storage in Docker Volumes:** Data extracted by workers is stored in Docker volumes to facilitate its access from other services and guarantee its persistence over time.
  - *Contribution to efficient data handling:* Storing data in Docker volumes allows fast and efficient access to data from any system component. This reduces latency and improves performance compared to storing on external file systems or databases.
  - *Integration with other components:* Docker volumes provide an abstraction layer for data, simplifying integration with other services, such as Elasticsearch and Neo4j databases.

- **2. Distributed processing system (Spark):**
 To enrich the information collected from the scientific papers, a process using Apache Spark is implemented. The data stored in the Docker volumes are accessed by the Spark cluster nodes, allowing distributed and efficient processing.

  - *Scalability:* Spark can easily scale from a single machine to thousands of nodes, allowing it to process large amounts of data efficiently. This scalability is essential for handling the high volume of scientific article data and complementary information from multiple APIs.
  - *Fault tolerance:* Spark's resilient distributed datasets (RDD) and DataFrame APIs provide built-in fault tolerance. If a node fails during processing, Spark can recompute the lost data using lineage information, ensuring reliable processing tasks.
  - *Performance:* By distributing tasks across multiple nodes, Spark can perform processing in parallel, which significantly reduces the time required for data transformation and analysis. This is crucial to meet the performance requirements of big data applications. 

- **3. Data storage:**
  The extracted data is initially stored in a Docker volume named "data," then processed in a simulated distributed system using Spark, and finally stored in multiple databases.

## Ensuring Data Availability

Ensuring data availability is critical in big data infrastructures to maintain the reliability and accessibility of information. In our project, we use several strategies and technologies to ensure that data remains available even in the face of hardware failures or other disruptions. 

ElasticSearch implements data replication by allowing each index to have one or more replica shards in addition to the primary shard, stored on different nodes in the cluster. If a node fails, a replica shard can be promoted to primary, ensuring data accessibility. Neo4j supports replication across clusters, where data is replicated to multiple instances, ensuring high availability and fault tolerance. 

MySQL uses master-slave replication, where the master database handles write operations and propagates changes to slave databases; in case of failure, a slave can be promoted to master, maintaining availability.

Distributing data and processing tasks across multiple nodes allows our infrastructure to tolerate failures without significant interruptions. Both Spark and ElasticSearch reroute tasks and data to healthy nodes in the event of failures, ensuring continuous operation. Regular backups of data stored in Neo4j, MySQL and ElasticSearch ensure that data can be restored in the event of catastrophic failures, using automated backup strategies to minimize data loss and downtime.

Load balancing in ElasticSearch distributes search and indexing requests across cluster nodes, avoiding bottlenecks and ensuring consistent performance. In MySQL, load balancers distribute queries to multiple instances, optimizing resource usage and maintaining high availability by preventing single-instance overload. These combined strategies ensure that our big data system is robust, resilient to failures, scalable and capable of handling large volumes of data with high availability and performance.

## Ensuring Data Scalability

Horizontal scalability is achieved with Apache Spark, whose architecture allows more worker nodes to be added to the cluster, distributing the data load and complex processing tasks. ElasticSearch also scales horizontally by adding more nodes to the cluster, distributing search and indexing tasks, allowing it to handle increasing loads efficiently. Neo4j can scale horizontally by adding more nodes to distribute the workload of the graph database, handling larger datasets and more complex queries.

MySQL, while primarily scaling horizontally, also supports vertical scalability through the use of more powerful hardware, such as CPUs and memory, which helps handle larger datasets and more complex queries within a single instance. 
ElasticSearch supports elastic scalability, allowing nodes to be dynamically added or removed based on current load and data volume, adjusting resource allocation in real time. Spark can also allocate resources dynamically, scaling up during processing peaks and scaling down during idle periods, thus optimizing resource usage and costs.

Cluster management is facilitated by tools such as Kubernetes, which can manage Spark and ElasticSearch clusters, automating the deployment, scaling and operation of containerized applications, ensuring efficient resource utilization. Continuous monitoring of resource usage and performance metrics allows the system to automatically scale resources according to predefined thresholds, ensuring optimal performance and availability.

## Efficiency in Data Processing

### Apache Spark:

- **In-Memory Processing:** Spark's ability to perform in-memory computations significantly reduces the time required for iterative processing tasks, such as those related to data extraction, transformation and analysis. This leads to faster execution compared to disk-based processing systems.
- **Parallel Processing:** By distributing tasks across multiple job nodes, Spark leverages parallel processing, which improves the speed and efficiency of data processing workflows.
- **Optimized Execution Plans:** Spark's Catalyst optimizer generates optimized execution plans for data queries, ensuring efficient use of computational resources and reducing processing time.

### ElasticSearch:

- **Efficient Indexing:** ElasticSearch's efficient indexing mechanisms, such as inverted indexes, ensure that data is stored in a manner that enables fast search and retrieval, minimizing the time and computational resources required to perform search queries.
- **Compression:** ElasticSearch employs compression techniques to reduce the storage footprint of indexed data, ensuring efficient use of disk space while maintaining fast access times.

### Neo4j:

- **Compact Graph Representation:** Neo4j's native graph storage engine is designed to store relationships as top-level entities, enabling compact and efficient storage of complex data relationships.
- **Efficient Traversal:** Neo4j's traversal algorithms are optimized for graph structures, enabling fast exploration of connected data, which is critical for analyzing relationships between scientific papers, publishers, and topics.

### MySQL:

- **Normalized Data Storage:** By using normalized schemas, MySQL minimizes data redundancy, leading to efficient use of storage space and maintaining data integrity.
- **Indexing:** MySQL supports various indexing strategies, such as B-trees and hashing, which improve the speed of data retrieval operations.

## Data Retrieval Efficiency

#### ElasticSearch:

- **Full-Text Search Capabilities:** ElasticSearch's powerful full-text search capabilities enable fast and accurate retrieval of documents based on text queries.
- **Relevance Scoring and Query Optimization:** ElasticSearch's relevance scoring and query optimization features ensure that the most relevant search results are returned quickly, improving the user experience and reducing the computational load on the system.

#### Neo4j:

- **Cypher Query Language:** Neo4j's Cypher query language is designed specifically for graph databases, enabling efficient and expressive querying of graph data.
- **Graph Algorithms:** Neo4j's built-in graph algorithms are optimized for performance, enabling efficient analysis of large graph data sets.

### Load Balancing:

- **ElasticSearch:** Load balancing between nodes ensures that no node becomes a bottleneck, evenly distributing the search and indexing load.

- **Use of Multiple Workers:** The implementation of multiple workers distributes the data extraction workload, allowing for more efficient and faster processing. This ensures more effective use of available resources and reduces overall data extraction time.

- The choice to use Docker containers provides a lightweight and efficient environment for running applications. By sharing the same kernel as the host operating system, containers minimize overhead and allow for greater portability of applications between different environments.

- **Data Storage in Docker Volumes:** By choosing to store data in Docker volumes, data access is optimized and latency is reduced. This improves the efficiency of read and write operations compared to access over a network.

## Project Scope

The scope of the project encompasses several stages and technologies, designed to create a robust and scalable infrastructure for scientific data mining, processing, analysis and storage. The key components and capabilities of the project are described below:

### Initial Data Extraction

- **Implementation of Docker Workers**: Configuration and deployment of four Docker containers, each running Python scripts to extract data in JSON format from a scientific article API.
- **Process Parallelization**: Use of multiple API keys to distribute and parallelize the extraction process, optimizing data collection time and efficiency.

### Data Merging and Consolidation

- Merging of the JSON files generated by the different workers into a single JSON file, ensuring a complete and accurate consolidation of the information collected.

### Data Processing with Apache Spark

- **Spark Cluster Deployment**: Setting up a Spark cluster with a master and six worker nodes to handle distributed data processing.
- **Data Enrichment**: Extracting additional information from other API sources, including details about the location, publisher, and main topic of each article.
- **CSV File Generation**: Transformation and storage of enriched data in CSV files, facilitating their later use in databases and other applications.

### Data Storage and Management

- **Neo4j Database**: Implementation of a Neo4j graph database for modeling and querying complex relationships between entities such as authors, articles and publishers.
- **MySQL Database**: Structured data storage in a MySQL relational database, allowing efficient queries and management of large volumes of information.
- **Elasticsearch**: Storage of JSON files in Elasticsearch, providing advanced full-text search and analysis capabilities.

### Data Visualization and Analysis

- **Integration with JupyterLab**: Use of JupyterLab to provide an interactive data analysis environment, allowing researchers to explore and visualize data efficiently.
- **Interactive Analysis**: Capabilities to perform interactive data analysis, including ad hoc queries, report generation, and visualization of graphs and relationships.

### Scalability and Scalability

- **Horizontal Scalability**: Ability to add more Docker workers and Spark nodes to handle larger data volumes or increase processing speed as needed.
- **Modularity**: Modular design that allows integration of new data sources and expansion of functionality without affecting the core system.

## Installation

Clone the repository using Git. Open your terminal or command prompt and run the following command:

```bash
git clone https://github.com/bnvulpe/PapersLab.git --config core.autocrlf=false
```
## Use

After cloning the repository, navigate to the project directory in your terminal or command prompt.

Once located in the docker-configuration folder:
```bash
cd docker-configuration
```

In GIT BASH:
```bash

1. export PWD_PARENT=$(dirname "$(pwd)")

2. docker build -t docker_configuration .

3. docker run -d --name docker_configuration -v PWD_PARENT:/app/project docker_configuration

4. docker cp $(docker ps -a --filter "name=docker_configuration" --format "{{.ID}}"):/app/docker-compose.yml $(dirname "$(pwd)")

5. cd ..

6. docker-compose up --build --detach

7. docker-compose stop
```
Once we have verified that the file all_data.json in dfs folder and stopped the container.

```bash

1. cd spark

2. ./build.sh

3. docker-compose --env-file .env up --build --detach

4. once all the data has been extracted (jupyter reports in logs): 

docker stop $(docker ps -a --format "{{.ID}} {{.Names}}" | grep "spark" | awk '{print $1}')

5. cd ../databases

6. docker compose up -d

Once jupyter has imported the data to Elasticsearch (jupyter reports it in logs), in the address localhost:8889 we will find Elasticsearch to make the necessary queries for the processing and analysis of the data at convenience. To work with Neo4j you must access localhost:7687, login with neo4j/password and make the imports of the file /databases/init.txt.

```
To disassemble everything in root run

```
./teardown.sh
```
## License

This project is licensed under the MIT License - see file [LICENSE](LICENSE) for more details.
