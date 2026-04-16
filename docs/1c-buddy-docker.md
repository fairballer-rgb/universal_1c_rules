# Развертывание 1c-buddy через Docker

Источник: [JohnyDeath/1c-buddy](https://github.com/JohnyDeath/1c-buddy)

## Предусловия

- Установлен Docker Desktop / Docker Engine.
- Получен токен `ONEC_AI_TOKEN` на `https://code.1c.ai`.

## Быстрый запуск

```bash
docker pull roctup/1c-buddy
docker run -d --name 1c-buddy --restart unless-stopped -p 6002:6002 -e "ONEC_AI_TOKEN=<your_1c_ai_token>" roctup/1c-buddy
```

Если нужен OpenAI-compatible endpoint:

```bash
docker pull roctup/1c-buddy
docker run -d --name 1c-buddy --restart unless-stopped -p 6002:6002 -e "ONEC_AI_TOKEN=<your_1c_ai_token>" -e "OPENAI_COMPAT_API_KEY=<your_custom_api_key>" roctup/1c-buddy
```

## Проверка

1. Проверить контейнер:
```bash
docker ps --filter "name=1c-buddy"
```

2. Проверить, что endpoint отвечает:
```bash
curl -i http://localhost:6002/mcp
```

3. Открыть UI:
- `http://localhost:6002/chat`

## Обновление

```bash
docker stop 1c-buddy
docker rm 1c-buddy
docker pull roctup/1c-buddy
docker run -d --name 1c-buddy --restart unless-stopped -p 6002:6002 -e "ONEC_AI_TOKEN=<your_1c_ai_token>" roctup/1c-buddy
```

## Типовые проблемы

- Порт `6002` занят: смените проброс порта (`-p 16002:6002`) и исправьте MCP URL.
- `401/403` от сервиса: проверьте `ONEC_AI_TOKEN`.
- Контейнер не стартует: посмотрите логи:
```bash
docker logs 1c-buddy
```
