FROM postgres:12.0
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
                              apt-utils \
                              net-tools \
                              sudo \
                              nano \
                              tzdata
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
USER postgres
