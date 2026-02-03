# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY apps/mobile/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY apps/mobile .

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install production dependencies only
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app .

# Expose port (for web preview)
EXPOSE 3000

# Default command - can be overridden
CMD ["npm", "start"]
