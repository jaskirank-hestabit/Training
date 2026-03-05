# Base image
FROM node:20-alpine

# Create working directory inside container
WORKDIR /app

# Copy package files first (for Docker layer caching)
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy rest of the application code
COPY . .

# Expose server port
EXPOSE 5000

# Start the Node server
CMD ["node", "server.js"]