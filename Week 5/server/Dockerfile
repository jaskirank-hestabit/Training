# Base image
FROM node:20-alpine

# Create working directory inside container
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy rest of code
COPY . .

# Expose port
EXPOSE 5000

# Start server
CMD ["node", "server.js"]