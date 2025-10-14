FROM node:20-alpine
WORKDIR /app

# Copy manifests first to leverage Docker layer caching
COPY package.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/ui/package.json packages/ui/package.json

# Install workspace deps at root so shared packages resolve peers (react, etc.)
RUN npm install

# Copy sources
COPY apps/web apps/web
COPY packages/ui packages/ui

# Build web workspace
RUN npm run --workspace web build

EXPOSE 3000
CMD ["npm", "run", "--workspace", "web", "start"]
