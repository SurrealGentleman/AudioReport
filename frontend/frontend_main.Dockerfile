# Базовый образ
FROM node:18 AS build

# Рабочая директория
WORKDIR /app

# Копируем package.json и package-lock.json
COPY . .

# Устанавливаем зависимости
RUN npm install

# Собираем приложение
# RUN npm run build

# Финальный образ с nginx
# FROM nginx:alpine

# Копируем собранные файлы из builder в nginx
# COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфиг nginx (если нужен)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 5173

# Запускаем nginx
# CMD ["nginx", "-g", "daemon off;"]
CMD ["npm", "run", "dev"]
