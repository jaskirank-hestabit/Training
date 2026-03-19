FROM node:18

WORKDIR /app

COPY package*.json ./
RUN npm install

# Accept build argument
ARG ENV_FILE

COPY . .

# Copy correct env file
COPY ${ENV_FILE} .env

EXPOSE 3000

ENV PORT=3000

CMD ["npm", "start"]