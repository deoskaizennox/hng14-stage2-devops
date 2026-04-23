# Stage 1: Install dependencies
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --production && npm cache clean --force

# Stage 2: Production runtime
FROM node:18-alpine
WORKDIR /app

# Non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S appuser -u 1001

# Copy node_modules first
COPY --from=builder --chown=appuser:nodejs /app/node_modules ./node_modules

# Copy all app files
COPY --chown=appuser:nodejs . .

USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

EXPOSE 3000
CMD ["node", "app.js"]
