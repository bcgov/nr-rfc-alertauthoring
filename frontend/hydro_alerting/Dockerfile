# Build static files
# Node Bullseye has npm
FROM node:20.12.2-bullseye-slim AS build

# Install packages, build and keep only prod packages
WORKDIR /app
COPY *.json *.ts ./
COPY ./src ./src
# remove --omit=dev because then ng required for build won't exist
RUN npm ci --ignore-scripts --no-update-notifier  && \
    npm run build

# Deploy container
# Caddy serves static files
FROM caddy:2.7.6-alpine
RUN apk add --no-cache ca-certificates curl

# Copy static files and run formatting
COPY --from=build /app/dist/browser /srv
COPY Caddyfile /etc/caddy/Caddyfile
RUN caddy fmt --overwrite /etc/caddy/Caddyfile

# Ports, health check and non-root user
EXPOSE 3000 3001
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost/:3001/health
USER 1001
