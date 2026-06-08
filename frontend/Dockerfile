FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build for production
RUN npm run build

# Expose port
EXPOSE 5173

# Run with preview (or serve with static server)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]