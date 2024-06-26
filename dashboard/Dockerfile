FROM debian:buster AS builder

WORKDIR /app

# generate Web certificate
RUN apt-get update && \
    apt-get install -y openssl && \
     mkdir -p python && \
    openssl req -newkey rsa:2048 -new -nodes -x509 \
    -days 3650 -subj "/C=DE/ST=Brake/L=lower Saxony/O=stko/OU=IT Department/CN=koehlers.de" \
    -keyout python/key.pem -out python/server.pem

# Use the official lightweight Python 3.11-slim image
FROM python:3.11-slim

WORKDIR /app
COPY static ./static
ADD "https://cdn.jsdelivr.net/npm/@mdi/font@3.x/css/materialdesignicons.min.css" ./static/libs/
#ADD "https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900|Material+Icons" ./static/libs/
ADD "https://cdn.jsdelivr.net/npm/vuetify@1.5.20/dist/vuetify.min.css" ./static/libs/
ADD "https://cdn.jsdelivr.net/npm/babel-polyfill/dist/polyfill.min.js" ./static/libs/
ADD "https://cdn.jsdelivr.net/npm/vue@2.x/dist/vue.js" ./static/libs/
ADD "https://cdn.jsdelivr.net/npm/vuetify@1.5.20/dist/vuetify.min.js" ./static/libs/


#ADD "https://cdn.jsdelivr.net/npm/@mdi/font@3.x/fonts/materialdesignicons-webfont.eot?v=3.9.97" ./static/fonts/materialdesignicons-webfont.eot
ADD "https://fonts.gstatic.com/s/materialicons/v142/flUhRq6tzZclQEJ-Vdg-IuiaDsNZ.ttf" ./static/fonts/
ADD "https://cdn.jsdelivr.net/npm/@mdi/font@3.x/fonts/materialdesignicons-webfont.eot?#iefix&v=3.9.97" ./static/fonts/materialdesignicons-webfont.eot
ADD "https://cdn.jsdelivr.net/npm/@mdi/font@3.x/fonts/materialdesignicons-webfont.woff2?v=3.9.97" ./static/fonts/materialdesignicons-webfont.woff2
ADD "https://cdn.jsdelivr.net/npm/@mdi/font@3.x/fonts/materialdesignicons-webfont.woff?v=3.9.97" ./static/fonts/materialdesignicons-webfont.woff
ADD "https://cdn.jsdelivr.net/npm/@mdi/font@3.x/fonts/materialdesignicons-webfont.ttf?v=3.9.97" ./static/fonts/materialdesignicons-webfont.ttf
COPY python ./python

COPY --from=builder /app/python/*.pem ./python/

COPY installdockers.sh /tmp/installdockers.sh
RUN chmod +x /tmp/installdockers.sh
RUN /usr/local/bin/python3 -m pip install --upgrade pip
RUN pip install -r python/requirements.txt
RUN bash -c "/tmp/installdockers.sh"


WORKDIR /app/python

CMD [ "python3", "./canspy_dashboard.py"  ]

EXPOSE 80
