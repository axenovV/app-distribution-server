# Настройка Timeweb Cloud S3

Инструкция по подключению вашего S3-совместимого хранилища Timeweb Cloud к App Distribution Service.

## Ваши данные

- **Endpoint**: `https://s3.twcstorage.ru`
- **Bucket name**: `2cd05a30-3217a1a2-5ae0-41c3-9625-213ca2776258`
- **Access Key**: `GRO9ATXSXK3YY9D7V4KW`
- **Secret Key**: `2UGmZaiY7cQTw0DSL4F5ALO3YxkmqG9blaJdUoSM`

## Настройка переменных окружения

### Для локальной разработки

Создайте файл `.env` в корне проекта или экспортируйте переменные:

```bash
export STORAGE_URL="s3://2cd05a30-3217a1a2-5ae0-41c3-9625-213ca2776258"
export AWS_ACCESS_KEY_ID="GRO9ATXSXK3YY9D7V4KW"
export AWS_SECRET_ACCESS_KEY="2UGmZaiY7cQTw0DSL4F5ALO3YxkmqG9blaJdUoSM"
export AWS_ENDPOINT_URL="https://s3.twcstorage.ru"
export AWS_REGION="ru-1"
export UPLOADS_SECRET_AUTH_TOKEN="your-secret-token-here"
export APP_BASE_URL="http://localhost:8000"
```

### Для Docker

```bash
docker run \
  -p 8000:8000 \
  -e STORAGE_URL="s3://2cd05a30-3217a1a2-5ae0-41c3-9625-213ca2776258" \
  -e AWS_ACCESS_KEY_ID="GRO9ATXSXK3YY9D7V4KW" \
  -e AWS_SECRET_ACCESS_KEY="2UGmZaiY7cQTw0DSL4F5ALO3YxkmqG9blaJdUoSM" \
  -e AWS_ENDPOINT_URL="https://s3.twcstorage.ru" \
  -e AWS_REGION="ru-1" \
  -e UPLOADS_SECRET_AUTH_TOKEN="your-secret-token-here" \
  -e APP_BASE_URL="https://your-domain.com" \
  ghcr.io/significa/app-distribution-server
```

### Для docker-compose

Создайте файл `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app-distribution:
    image: ghcr.io/significa/app-distribution-server
    ports:
      - "8000:8000"
    environment:
      - STORAGE_URL=s3://2cd05a30-3217a1a2-5ae0-41c3-9625-213ca2776258
      - AWS_ACCESS_KEY_ID=GRO9ATXSXK3YY9D7V4KW
      - AWS_SECRET_ACCESS_KEY=2UGmZaiY7cQTw0DSL4F5ALO3YxkmqG9blaJdUoSM
      - AWS_ENDPOINT_URL=https://s3.twcstorage.ru
      - AWS_REGION=ru-1
      - UPLOADS_SECRET_AUTH_TOKEN=your-secret-token-here
      - APP_BASE_URL=https://your-domain.com
```

## Проверка подключения

После запуска сервера попробуйте загрузить тестовое приложение:

```bash
curl -X "POST" \
  "http://localhost:8000/upload" \
  -H "Accept: application/json" \
  -H "X-Auth-Token: your-secret-token-here" \
  -H "Content-Type: multipart/form-data" \
  -F "app_file=@your-app-build.ipa"
```

Если все настроено правильно, вы получите ссылку на страницу установки.

## Важные замечания

1. **Безопасность**: Обязательно измените `UPLOADS_SECRET_AUTH_TOKEN` на свой секретный токен!

2. **Bucket должен существовать**: Убедитесь, что бакет `2cd05a30-3217a1a2-5ae0-41c3-9625-213ca2776258` уже создан в вашем Timeweb Cloud аккаунте.

3. **Права доступа**: Убедитесь, что предоставленные ключи доступа имеют права на чтение и запись в указанный бакет.

4. **CORS настройки**: Если вы планируете предоставлять публичный доступ к файлам через браузер, настройте CORS политику на вашем S3 хранилище.

5. **APP_BASE_URL**: Установите правильный публичный URL вашего сервера для корректной генерации ссылок на загруженные приложения.

## Регион

Если регион `ru-1` не подходит, попробуйте другие варианты:
- `ru-2`
- `us-east-1` (если Timeweb использует стандартные регионы AWS)
- Оставьте пустым, если регион не требуется

## Устранение неполадок

Если возникают проблемы с подключением:

1. Проверьте, что все переменные окружения установлены правильно
2. Убедитесь, что бакет существует и доступен
3. Проверьте права доступа ключей
4. Проверьте логи приложения на наличие ошибок подключения к S3

