# ── Stage 1: Build ────────────────────────────────────────────
FROM node:18 AS builder
 
WORKDIR /app
 
COPY package*.json ./
RUN npm install
 
ARG ENV_FILE
COPY . .
COPY ${ENV_FILE} .env
 
RUN npm run build
 
# ── Stage 2: Serve with lightweight static server ─────────────
FROM node:18-slim
 
RUN npm install -g serve
 
WORKDIR /app
 
COPY --from=builder /app/build ./build
 
EXPOSE 3000
 
CMD ["serve", "-s", "build", "-l", "3000"]