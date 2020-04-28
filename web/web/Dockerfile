FROM conda/miniconda3-centos7

WORKDIR /web

COPY . /web/

RUN chmod +x *.sh
RUN ./setup.sh

EXPOSE 5000/tcp