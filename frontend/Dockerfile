FROM node:21.7.1-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . ./
RUN npm run build

# Copy the built React files to /staticfiles at container startup
CMD cp -r /app/build/* /staticfiles/
