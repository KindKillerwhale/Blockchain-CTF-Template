FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update --fix-missing && apt-get -y upgrade

RUN apt-get -y install \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    socat \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

RUN npm install -global ganache

ADD . /home/ctf
WORKDIR /home/ctf

RUN python3 -m pip install --upgrade pip

RUN pip3 install flask[async] web3 dataclasses typing

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
