# Подключение библиотек БСП

Для универсальных правил нужно иметь локальный код БСП обеих линеек:
- `ssl_3_1`
- `ssl_3_2`

## Вариант 1: обычный clone

Из каталога `universal_1c_rules/vendor`:

```bash
git clone https://github.com/1c-syntax/ssl_3_1.git ssl_3_1
git clone https://github.com/1c-syntax/ssl_3_2.git ssl_3_2
```

## Вариант 2: submodule

Из корня репозитория, куда копируется комплект:

```bash
git submodule add https://github.com/1c-syntax/ssl_3_1.git vendor/ssl_3_1
git submodule add https://github.com/1c-syntax/ssl_3_2.git vendor/ssl_3_2
git submodule update --init --recursive
```

## Как выбрать линейку БСП

- Выбор делайте по фактической версии БСП в вашей конфигурации.
- Обычно:
  - БСП `3.1.x` -> `ssl_3_1`
  - БСП `3.2.x` -> `ssl_3_2`
- Точное соответствие уточняйте по релизу в метаданных вашей выгрузки.

## Рекомендация по git

Полные клоны `ssl_3_1` и `ssl_3_2` обычно тяжелые. Если комплект хранится в общем репозитории команды, лучше подключать их через `submodule` или локальным clone без коммита содержимого.
