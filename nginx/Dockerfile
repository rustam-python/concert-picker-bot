FROM nginx:1.17.2

MAINTAINER Rustam Aliev

ENV TZ=Europe/Moscow

RUN dpkg-reconfigure -f noninteractive tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY .htpasswd /etc/nginx/.htpasswd
COPY .uruk_htpasswd /etc/nginx/.uruk_htpasswd
