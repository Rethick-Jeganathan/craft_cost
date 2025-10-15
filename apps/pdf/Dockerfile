FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --production
COPY src ./src
# Run as non-root user
RUN addgroup -S app && adduser -S app -G app -u 10001 && chown -R app:app /app
USER app
EXPOSE 4000
CMD ["npm", "start"]
