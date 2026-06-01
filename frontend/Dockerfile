FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Expose port for Vite
EXPOSE 5173

# Start development server binding to all network interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
