FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy app source
COPY . .

# Build app
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
