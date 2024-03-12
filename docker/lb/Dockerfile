FROM ubuntu:jammy

RUN apt-get -q -y update && DEBIAN_FRONTEND=noninteractive apt-get -q -y upgrade
RUN apt-get -q -y install nginx

COPY docker/lb/nginx.conf /etc/nginx/nginx.conf
COPY docker/lb/phenome10k.org.conf /etc/nginx/conf.d/phenome10k.org.conf

CMD ["nginx", "-g", "daemon off;"]
