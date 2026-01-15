FROM node:20-alpine as builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine

# вычищаем дефолтный конфиг, чтобы никто случайно не экспонировал этот nginx наружу
RUN rm -f /etc/nginx/conf.d/default.conf

# кладём статические файлы фронта из builder
COPY --from=builder /app/dist /usr/share/nginx/html
