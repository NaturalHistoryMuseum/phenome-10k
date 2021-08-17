FROM node:14.5

COPY ./package.json /var/phenome-10k/www/package.json
COPY ./package-lock.json /var/phenome-10k/www/package-lock.json
COPY ./build /var/phenome-10k/www/build
COPY ./node /var/phenome-10k/www/node

WORKDIR /var/phenome-10k/www

# https://github.com/npm/npm/issues/17346#issuecomment-313783304
RUN npm config set unsafe-perm
RUN npm i
RUN npm run build

CMD ["npm", "run", "watch"]
