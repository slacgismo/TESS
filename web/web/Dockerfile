FROM conda/miniconda3-centos7

WORKDIR /tmp

COPY setup.sh /tmp/
COPY requirements.txt /tmp/

RUN chmod +x *.sh
RUN ./setup.sh

EXPOSE 5000/tcp