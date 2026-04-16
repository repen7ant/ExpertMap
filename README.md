# Гайд по использованию

## 1. Создать .env

```bash
mv .env.example .env
```

## 2. Запустить проект

```bash
docker-compose up -d --build
```

## 3. Заполнить бд моковыми данными:

```bash
docker compose exec fastapi uv run python -m app.db.seed
```

## 4. Разработка

После запуска API будет доступно по адресу:

```bash
http://localhost:8000
```

Swagger:

```bash
http://localhost:8000
```

Логи бэкенда:

```bash
docker compose logs fastapi -f
```

## 5. Остановка проекта

```bash
docker compose down
```

С удалением данных:

```bash
docker compose down -v
```
