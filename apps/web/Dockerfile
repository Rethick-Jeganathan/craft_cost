FROM node:20-alpine
WORKDIR /app

# Copy manifests first to leverage Docker layer caching
COPY package.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/ui/package.json packages/ui/package.json

# Install web deps (resolves local file: ../../packages/ui)
RUN npm install --prefix apps/web --production=false

# Copy sources
COPY apps/web apps/web
COPY packages/ui packages/ui

# Build web
RUN npm run build --prefix apps/web

EXPOSE 3000
CMD ["npm", "--prefix", "apps/web", "run", "start"]
