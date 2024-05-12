FROM debian:buster AS builder

WORKDIR /app

# generate Web certificate
RUN apt-get update && \
    apt-get install -y openssl && \
     mkdir -p python && \
    openssl req -newkey rsa:2048 -new -nodes -x509 \
    -days 3650 -subj "/C=DE/ST=Brake/L=lower Saxony/O=stko/OU=IT Department/CN=koehlers.de" \
    -keyout python/key.pem -out python/server.pem


#FROM python:3
FROM python:3-buster

WORKDIR /app
COPY static ./static
COPY python ./python

COPY --from=builder /app/python/*.pem ./python/

COPY installdockers.sh /tmp/installdockers.sh
RUN chmod +x /tmp/installdockers.sh
RUN /usr/local/bin/python3 -m pip install --upgrade pip
RUN pip install -r python/requirements.txt
RUN bash -c "/tmp/installdockers.sh"


WORKDIR /app/python

CMD [ "python3", "./canspy_dashboard.py" , "-s" ]

EXPOSE 8000
