# Stage: dev — hot-reload development server
FROM node:20-alpine AS dev

WORKDIR /app

COPY package.json ./
RUN npm install package
RUN npm i
COPY . .

EXPOSE 3001

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage: prod — static build served by nginx
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine AS prod

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
