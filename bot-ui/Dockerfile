# Use Node 20 as the base image
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# FIX: Added --legacy-peer-deps to ignore strict dependency conflicts
RUN npm install --legacy-peer-deps

# Copy the rest of the React code
COPY . .

EXPOSE 3000

# Changed from "npm start" to "npm run dev" because your project likely uses Vite.
# The -- --host flag ensures Vite is accessible from outside the Docker container.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]