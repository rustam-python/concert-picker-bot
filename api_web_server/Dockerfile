FROM ubuntu:19.04

MAINTAINER Rustam Aliev

WORKDIR /src/concert_picker
COPY /api_web_server /src/concert_picker
COPY /api-web-server-config.ini /src/concert_picker/api-web-server-config.ini
ENV TZ=Europe/Moscow
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
                              apt-utils \
                              sudo \
                              bash \
                              nano \
                              git \
                              net-tools \
                              tzdata \
    && echo $TZ > /etc/timezone && rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev python3-setuptools
RUN cd /usr/local/bin && \
    ln -s /usr/bin/python3 python
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install .