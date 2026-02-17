# Production Dockerfile for Next.js frontend
FROM node:20-slim as base

# Set working directory
WORKDIR /app

# Install dependencies first for better caching
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --production=false

# Copy the rest of the frontend source
COPY frontend/ ./

# Build the Next.js app
RUN npm run build

# Expose Next.js port
EXPOSE 3000

# Run in production mode
ENV NODE_ENV=production

CMD ["npm", "start"]
