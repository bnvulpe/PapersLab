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
jupyter nbconvert --execute --to notebook --inplace "/opt/workspace/"graph.ipynb""