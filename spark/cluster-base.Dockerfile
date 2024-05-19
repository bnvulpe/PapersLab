ARG debian_buster_image_tag=8-jre-slim
FROM openjdk:${debian_buster_image_tag}

# -- Layer: OS + Python 3.7

ARG shared_workspace=/opt/workspace

RUN mkdir -p ${shared_workspace} && \
    apt-get update -y || (sleep 30 && apt-get update -y) || (sleep 60 && apt-get update -y) && \
    apt-get install -y \
        curl \
        gcc \
        build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libsqlite3-dev \
        libgdbm-dev \
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        wget \
        libjpeg-dev \
        procps \
        vim \
        net-tools || \
        (sleep 30 && apt-get install -y \
        curl \
        gcc \
        build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libsqlite3-dev \
        libgdbm-dev \
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        wget \
        libjpeg-dev \
        procps \
        vim \
        net-tools) || \
        (sleep 60 && apt-get install -y \
        curl \
        gcc \
        build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libsqlite3-dev \
        libgdbm-dev \
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        wget \
        libjpeg-dev \
        procps \
        vim \
        net-tools) && \
    curl -O https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz && \
    tar -xf Python-3.7.3.tar.xz && \
    cd Python-3.7.3 && \
    ./configure && \
    make -j 8 && \
    make install && \
    rm -rf /var/lib/apt/lists/*

ENV SHARED_WORKSPACE=${shared_workspace}

# -- Runtime

VOLUME ${shared_workspace}
CMD ["bash"]
