FROM node:14.5

RUN apt-get update -y && apt-get install mysql-client -y

COPY ./docker/app-node/entrypoint /deploy/entrypoint
COPY ./web/package.json /var/phenome-10k/www/web/package.json
COPY ./web/package-lock.json /var/phenome-10k/www/web/package-lock.json

WORKDIR /var/phenome-10k/www/web

# https://github.com/npm/npm/issues/17346#issuecomment-313783304
RUN npm config set unsafe-perm
RUN npm i

ENTRYPOINT ["/bin/bash", "/deploy/entrypoint"]

CMD ["npm", "run", "watch"]
