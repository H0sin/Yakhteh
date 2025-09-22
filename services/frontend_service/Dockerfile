# syntax=docker/dockerfile:1.7-labs

# ---- Stage 1: Build the Vite React application ----
FROM node:lts-alpine AS build-stage
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# ---- Stage 2: Serve the application with Nginx ----
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]