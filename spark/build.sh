SPARK_VERSION="3.4.0"
HADOOP_VERSION="3"
JUPYTERLAB_VERSION="3.4.8"

# -- Building the Images

docker build \
  -f cluster-base.Dockerfile \
  -t cluster-base .

docker build \
  -f spark-master.Dockerfile \
  -t spark-master .

docker build \
  -f spark-worker.Dockerfile \
  -t spark-worker .

docker build \
  --build-arg spark_version="${SPARK_VERSION}" \
  --build-arg jupyterlab_version="${JUPYTERLAB_VERSION}" \
  -f jupyterlab.Dockerfile \
  -t jupyterlab .


