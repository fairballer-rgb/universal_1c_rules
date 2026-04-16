# universal_1c_rules

Переносимый комплект правил и скилов для Cursor под проекты 1С.

Примечание: комплект изначально разрабатывался под Cursor. В Claude Code те же принципы применимы, но поведение может отличаться из-за различий в механике правил и "скилов". Рекомендованный порядок для Claude Code описан в [`docs/claude-code.md`](docs/claude-code.md).

Цель комплекта:
- использовать проверенные источники (документация платформы, ИТС, локальный код БСП, код проекта),
- уменьшать расход токенов за счет коротких always-on правил и точечной подгрузки контекста,
- стабильно работать в любых конфигурациях 1С.

## Состав

- [`.cursor/rules/`](.cursor/rules/) - правила маршрутизации, навигации, БСП, MCP, типографики.
- [`.cursor/skills/`](.cursor/skills/) - набор прикладных скилов для задач 1С.
- [`docs/`](docs/) - документация по разворачиванию onec-buddy, настройке MCP и проверке сценариев.
- [`vendor/README.md`](vendor/README.md) - как подключить `ssl_3_1` и `ssl_3_2`.
- [`project-map/generate-map.py`](project-map/generate-map.py) - тонкая копия генератора карты проекта для автономного запуска.

## Быстрая установка

1. Скопировать содержимое [`universal_1c_rules/.cursor/`](universal_1c_rules/.cursor/) в [`.cursor/`](.cursor/) целевого проекта.
2. Поднять `1c-buddy` по [`docs/1c-buddy-docker.md`](docs/1c-buddy-docker.md).
3. Добавить MCP-конфиг из [`docs/mcp-cursor.sample.json`](docs/mcp-cursor.sample.json) в пользовательские настройки Cursor.
   Для Claude Code (с MCP): см. [`docs/claude-code.md`](docs/claude-code.md).
4. Подключить БСП (`ssl_3_1`/`ssl_3_2`) по [`vendor/README.md`](vendor/README.md).
5. При необходимости сгенерировать карту проекта ([`project-map`](project-map/)) по [`docs/project-map-regeneration.md`](docs/project-map-regeneration.md).

## Принципы универсальности

- Никаких жестких связок "тип продукта -> версия БСП".
- Линейка БСП выбирается по фактической версии библиотеки в вашей выгрузке.
- Ядро правил использует `project-map` как механизм навигации, а не продукт-специфичные таблицы.

## Проверка после установки

Используйте чеклист [`docs/validation-checklist.md`](docs/validation-checklist.md) и прогоните 4 эталонных запроса из ТЗ.

## Благодарности

При создании комплекта использованы и адаптированы материалы и инструменты из следующих публичных источников:

- [JohnyDeath/1c-buddy](https://github.com/JohnyDeath/1c-buddy) - MCP-инструменты для работы с документацией платформы/ИТС и проверки BSL.
- [JohnyDeath/cc-1c-skills](https://github.com/JohnyDeath/cc-1c-skills) - upstream-набор скилов, который лег в основу состава [`.cursor/skills`](.cursor/skills/).
- [comol/cursor_rules_1c](https://github.com/comol/cursor_rules_1c) - upstream-набор правил и подходов, использованный как отправная точка и затем адаптированный под универсальный контур.
- [1c-syntax/ssl_3_1](https://github.com/1c-syntax/ssl_3_1) и [1c-syntax/ssl_3_2](https://github.com/1c-syntax/ssl_3_2) - исходники БСП для поиска готовых решений и примеров по коду.

## Лицензия

Код и материалы этого репозитория распространяются по лицензии MIT, см. файл [`LICENSE`](LICENSE).

Зависимости и сторонние репозитории, которые вы подключаете отдельно (например, БСП в `vendor/ssl_3_1` и `vendor/ssl_3_2`), продолжают распространяться по их собственным лицензиям.
