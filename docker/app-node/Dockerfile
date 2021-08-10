FROM node:14

RUN apt-get update && apt-get install -y --no-install-recommends \
                mysql-client

COPY ./package.json /var/phenome10k/www/package.json
COPY ./package-lock.json /var/phenome10k/www/package-lock.json
COPY ./build /var/phenome10k/www/build
COPY ./node /var/phenome10k/www/node

WORKDIR /var/phenome10k/www

RUN npm i

CMD ["npm", "run", "watch"]
