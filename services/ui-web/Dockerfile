# Étape build
FROM node:20-alpine AS build
WORKDIR /app

COPY services/ui-web/package*.json ./
RUN npm ci

COPY services/ui-web .
COPY services/ui-web/.env-docker ./.env
RUN npm run build

# Étape runtime (serveur statique)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY services/ui-web/nginx.default.conf /etc/nginx/conf.d/default.conf

# optionnel : config nginx custom si tu veux gérer /api différemment
EXPOSE 80
