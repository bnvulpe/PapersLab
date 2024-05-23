#!/bin/bash

# Define the list of notebooks to execute
notebooks=(
  "text_classification.ipynb"
  "time_data.ipynb"
  "wiki-publishers.ipynb"
)

# Execute each notebook in parallel
for notebook in "${notebooks[@]}"; do
  jupyter nbconvert --execute --to notebook --inplace "/opt/workspace/$notebook" &
done

# Wait for all background processes to finish
wait
jupyter nbconvert --execute --to notebook --inplace "/opt/workspace/"graph.ipynb"" &
wait
jupyter nbconvert --execute --to notebook --inplace "/opt/workspace/"renaming.ipynb"" &

# Wait for all background processes to finish
wait
echo "All data has been extracted successfully! You can go on and build the databases."

# Wait for Elasticsearch to be available
while ! curl -s http://elasticsearch:9200 >/dev/null; do
  echo "Waiting for Elasticsearch..."
  sleep 5
done

echo "Elasticsearch is up and running!"

# Run the initialization notebook
jupyter nbconvert --execute --to notebook --inplace "/opt/workspace/"init_elasticdb.ipynb"" 

echo "Imported data to Elasticsearch successfully! You can access the /elasticsearch_queries in localhost:8889 to run some queries."