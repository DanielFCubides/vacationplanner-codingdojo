# Stage: dev — hot-reload development server
FROM node:20-alpine AS dev

WORKDIR /app

COPY package.json ./
RUN npm install
COPY . .

EXPOSE 3001

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage: prod — static build served by nginx
FROM node:20-alpine AS build

WORKDIR /app

ARG VITE_AUTH_BACKEND_URL
ENV VITE_AUTH_BACKEND_URL=${VITE_AUTH_BACKEND_URL}

COPY package.json ./
RUN npm install

COPY . .
RUN test -n "$VITE_AUTH_BACKEND_URL" && npm run build

FROM nginx:alpine AS prod

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
