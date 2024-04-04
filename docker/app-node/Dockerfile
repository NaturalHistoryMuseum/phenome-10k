FROM node:14

RUN apt-get -q -y update && DEBIAN_FRONTEND=noninteractive apt-get -q -y upgrade
RUN apt-get -q -y install mariadb-client

COPY ./docker/app-node/entrypoint /deploy/entrypoint
COPY ./web/package.json /var/phenome-10k/www/web/package.json
COPY ./web/package-lock.json /var/phenome-10k/www/web/package-lock.json

WORKDIR /var/phenome-10k/www/web

# https://github.com/npm/npm/issues/17346#issuecomment-313783304
RUN npm config set unsafe-perm
RUN npm i

ENTRYPOINT ["/bin/bash", "/deploy/entrypoint"]

CMD ["npm", "run", "watch"]
