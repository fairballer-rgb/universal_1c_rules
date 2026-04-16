# Использование комплекта в Claude Code (MCP)

Этот комплект собран под Cursor, но основные принципы переносятся в Claude Code при включенном MCP.

## Ключевые отличия от Cursor

1. `.cursor/rules/*.mdc` в Claude Code не подключаются автоматически.
   Чтобы Claude стабильно следовал маршрутизации, правила нужно перенести в проектные инструкции (обычно файл `CLAUDE.md` в корне проекта).

2. `.cursor/skills/` в Claude Code не исполняются как "скилы" Cursor.
   Их можно использовать как библиотеку процедур: Claude читает `SKILL.md` по запросу или по вашей команде.

3. MCP подключается не через настройки Cursor, а через команды `claude mcp ...` (или через конфигурацию Claude Code).

## Рекомендуемый порядок действий

1) Поднять `1c-buddy` по инструкции `docs/1c-buddy-docker.md`.

2) Подключить MCP-сервер в Claude Code:

```bash
claude mcp add --transport http user-onec-buddy-mcp http://localhost:6002/mcp
```

Проверка:

```bash
claude mcp list
claude mcp get user-onec-buddy-mcp
```

Внутри Claude Code также можно проверить состояние через команду `/mcp`.

3) Добавить проектные инструкции для Claude (чтобы заменить `.cursor/rules/*.mdc`).
Минимальный состав, который стоит перенести:

- `.cursor/rules/agent_routing.mdc`
- `.cursor/rules/1c_buddy.mdc`
- `.cursor/rules/bsp_libraries.mdc`
- `.cursor/rules/architecture.mdc`
- `.cursor/rules/typography.mdc`
- `.cursor/rules/platform-solutions.mdc` (по желанию)

Практика: создайте `CLAUDE.md` в корне целевого проекта и вставьте туда выжимку из перечисленных файлов (или просто их содержимое, если объем устраивает).

4) Убедиться, что в проекте есть `project-map/` (или сгенерировать по `docs/project-map-regeneration.md`).

## Практические нюансы

- В Claude Code важно, чтобы MCP был подключен до первых запросов про платформенную документацию или ИТС.
- Для "как сделать X" по БСП сначала ориентируйтесь на локальные клоны `vendor/ssl_3_1` или `vendor/ssl_3_2`, затем на ИТС и документацию через `1c-buddy`.
- Для вопросов по конкретной конфигурации сначала используйте `project-map/PROJECT_MAP.md`, затем `project-map/subsystems/*.md`, затем точечные BSL/XML файлы.
