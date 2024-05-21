FROM spark-base

RUN sed -i 's|http://deb.debian.org/debian|http://ftp.us.debian.org/debian|g' /etc/apt/sources.list && \
    apt-get update -y || (sleep 30 && apt-get update -y) || (sleep 60 && apt-get update -y) && \
    apt-get install -y vim net-tools iputils-ping || \
    (sleep 30 && apt-get install -y --fix-missing vim net-tools iputils-ping) || \
    (sleep 60 && apt-get install -y --fix-missing vim net-tools iputils-ping) && \
    rm -rf /var/lib/apt/lists/*

# -- Runtime
ARG spark_master_web_ui=8080

EXPOSE ${spark_master_web_ui} ${SPARK_MASTER_PORT}

# Create the workspace/events shared dir and start Spark Master
CMD bash -c "mkdir -p /opt/workspace/events && mkdir -p /opt/workspace/dataout && bin/spark-class org.apache.spark.deploy.master.Master >> logs/spark-master.out"
