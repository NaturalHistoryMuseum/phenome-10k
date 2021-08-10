FROM centos:7

RUN yum -y update && yum -y upgrade
RUN yum install -y epel-release
RUN yum -y install nginx

COPY docker/lb/nginx.conf /etc/nginx/nginx.conf
COPY docker/lb/phenome10k.org.conf /etc/nginx/conf.d/phenome10k.org.conf

CMD ["nginx", "-g", "daemon off;"]
