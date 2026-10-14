# Запуск и проверки

Compose запускает фронтенд и бэкенд стенда: страница «карточка → атрибуты с цитатой и уверенностью
→ очередь проверки». Бэкенду нужен компактный пакет данных `data/stand/pack.json.gz` — он собирается
из подготовленных данных командой `stand-pack` (раздел [«Как поднять стенд?»](#как-поднять-стенд)).
Базы данных нет: очередь проверки и алиасы живут в памяти процесса.

**Читайте, если** вы запускаете шаблон · **Связано:** [архитектура](architecture.md) · [зависимости](dependencies.md)

## Как запустить через Docker?

Нужны Docker и Compose v2. Из корня репозитория:

```bash
cp .env.example .env
docker buildx bake
docker compose up
```

Интерфейс: http://localhost:8080, API: http://localhost:8000, Swagger: http://localhost:8000/docs.
Образы собирает только `docker-bake.hcl`; Compose берёт готовые образы
`<COMPOSE_PROJECT_NAME>-backend:<TAG>` и `<COMPOSE_PROJECT_NAME>-frontend:<TAG>` и не скачивает их
из реестра. Без сборки `docker compose up` остановится с ошибкой об отсутствующем образе.
Переменные контейнеров приходят из `.env` через `env_file`; без `.env` действуют значения по
умолчанию. Первичная сборка требует сети для загрузки зависимостей и образов.

Образ бэкенда по умолчанию собирается без SDK Claude и Codex. Чтобы включить `LANGUAGE_MODEL`,
соберите образ с флагом `LLM`:

```bash
LLM=true docker buildx bake
docker compose up
```

Переменные сборки (`LLM`, `TAG`, `SITE_URL`, `COMPOSE_PROJECT_NAME`) bake берёт из окружения, а не
из `.env`.

## Как разрабатывать без Docker?

Нужны Node.js 22.18+ или поддерживаемая более новая версия и npm.

```bash
cd frontend
npm ci
npm run dev
```

Адрес покажет Vite при запуске. Бэкенд без Docker, из корня:

```bash
cd backend
uv sync                      # группы dev и llm; без SDK LLM: uv sync --no-group llm
uv run uvicorn app.main:create_app --factory --reload
```

## Как подготовить данные?

Архив организаторов в git не хранится: 1,1 ГБ. Положите `dataset.zip` в `brief/sources/`, сверьте
SHA-256 с таблицей в `brief/sources/README.md` и распакуйте:

```bash
unzip brief/sources/dataset.zip -d data/raw
cd backend
uv run prepare-data --raw ../data/raw --out ../data/processed
```

Команда без сети и ключей пишет в `data/processed/`:

| Файл | Что внутри |
|---|---|
| `cards.parquet` | Карточка: `title`, `description`, название оффера, категория, продавец, параметры продавца без `*_search`, флаги `in_catalog`, `has_text`, `has_spec_block` |
| `gold.parquet` | Эталон: `sku_id`, атрибут, значение, единица — из параметров `*_search`, плюс бренд и модель оффера |
| `splits.parquet` | `train` / `val` / `test` по хешу `sku_id` с сидом 42 и `new_category` — отложенные целиком категории |
| `required_attributes.parquet` | Обязательные атрибуты категории: бренд, модель и до шести `*_search`, у которых карточки с атрибутом собирают от 30 % кликов категории; порядок — по доле кликов с упоминанием значения атрибута в запросе, вес — клики категории × (0,01 + эта доля) |
| `categories.parquet`, `clicks_sku.parquet`, `clicks_category.parquet` | Дерево категорий с путями, клики по SKU и по категориям |
| `stats.json` | Пересечения файлов, размеры сплитов, частые атрибуты, время прогона |

`skus.pkl` читается потоково, без `pickle.load`: читатель понимает только опкоды словарей, списков и
строк и падает на любом опкоде, который может исполнить код. Параметры `*_search` попадают только в
`gold.parquet`, это проверяет юнит-тест.

## Как получить предсказания и отчёт метрик?

После подготовки данных базлайн (справочники + правила) строится и оценивается одной командой:

```bash
cd backend
uv run baseline --data ../data/processed --out ../data/predictions --reports ../reports
```

Команда без сети и ключей строит справочники по `train`, извлекает атрибуты для карточек `test` и
`new_category` и пишет (`--splits val` — тот же прогон на настроечном сплите, отчёт `reports/baseline_val.md`):

| Файл | Что внутри |
|---|---|
| `data/predictions/baseline.predictions.jsonl` | По строке на карточку: `sku_id`, `category_id`, `split`, `confidence_calibrated: false`, `attributes: {атрибут: {value, confidence, source, sources, evidence, start, end}}` — значения с уверенностью от 0,35; `review` — то же для значений ниже порога, очередь проверки |
| `data/predictions/baseline.candidates.parquet` | Все кандидаты для следующих ступеней: `sku_id`, `attribute`, `key`, `value`, `evidence`, `start`, `end`, `source`, `zone`, `affinity`, `prior`, `seller_fit`, `slot`, `score`, `chosen` |
| `reports/baseline.md`, `reports/baseline.json` | Метрики по [плану валидации](validation-plan.md): сводка по срезам и таблицы по атрибутам |

Предсказания для всех 1,18 млн карточек с текстом, без оценки:

```bash
uv run baseline --data ../data/processed --out ../data/predictions --all-cards --no-candidates
```

Пишет `data/predictions/baseline_all.predictions.jsonl`. Без категории карточка получает только бренд
и цвет, поэтому сначала стоит восстановить категорию для карточек вне каталога:

```bash
uv run infer-categories --data ../data/processed --raw ../data/raw --reports ../reports
```

Команда без сети и ключей (~40 мин, пик ~3 ГБ, 3 ядра): берёт категорию из кликов (`sku_seo_id`), а
где кликов нет — из классификатора по названию; пишет `data/processed/inferred_categories.parquet`
(`sku_id`, `category_id`, `source`: `catalog` / `clicks` / `classifier`, `confidence`) и отчёт
`reports/category.md` с выбором порога, гистограммами уверенности и случайными примерами. Правила —
в [решениях](design-decisions.md#откуда-берётся-категория-у-карточки-вне-каталога). Базлайн с
`--all-cards` подхватывает эту таблицу сам; категория каталога всегда важнее.

Полный файл по всем карточкам быстрее собирать параллельно — 5 частей по `sku_id`, не больше трёх
процессов одновременно, под `nice`:

```bash
bash scripts/predict-all.sh ../data/processed ../data/predictions
```

Скрипт режет `cards.parquet` командой `uv run shard-cards` в `data/shards/`, считает части и склеивает
`data/predictions/baseline_all.predictions.jsonl`; предыдущий файл остаётся рядом как `.bak`.
`SHARDS` и `PARALLEL` в окружении меняют число частей и процессов.

### Двойники из каталога поверх ранжировщика

После `uv run ranker` (нужен `data/predictions/ranker.predictions.jsonl`):

```bash
uv run twins --data ../data/processed --out ../data/predictions --reports ../reports
```

Строит индекс названий карточек `train`, подбирает порог сходства на `val`, переносит значения
двойников в пустые обязательные слоты `test` и `new_category`. Пишет
`data/predictions/twins.predictions.jsonl` (формат ранжировщика; у перенесённых значений
`source: catalog_twin`, `twin_sku`, `similarity`, `exact_title`, `start`/`end` = −1) и
`reports/twins.md`/`.json` с абляцией «ранжировщик → + двойники». kNN считается в одном потоке
батчами разреженного умножения (`--knn-batch`, по умолчанию 256 запросов ≈ 200 МБ на батч), `--stage`
— файл предсказаний, поверх которого переносить.

## Как поднять стенд?

Стенд работает на том же коде извлечения, что и офлайн-базлайн, но не читает гигабайты parquet при
старте: ему нужен пакет на ~2 МБ со справочниками, обязательными атрибутами и примерами карточек.
После подготовки данных:

```bash
cd backend
uv run stand-pack --data ../data/processed --out ../data/stand/pack.json.gz
```

Команда без сети и ключей, около двух минут и 1,5 ГБ памяти, берёт 30 категорий с наибольшим числом
кликов (смартфоны и ноутбуки — всегда), строит по `train` справочники для их обязательных атрибутов и
выбирает до 40 примеров из `test`, у которых часть значений уверенная, а часть уходит в очередь
проверки. `--categories` и `--examples` меняют эти числа. Пакет в git не хранится, как и остальные
данные.

Через Docker пакет монтируется в бэкенд только для чтения (`./data/stand` → `/srv/data/stand`):

```bash
docker buildx bake
docker compose up
```

Без Docker, из корня — бэкенд и фронтенд в двух терминалах:

```bash
cd backend && STAND_PACK=../data/stand/pack.json.gz uv run uvicorn app.main:create_app --factory
cd frontend && npm run dev
```

Без пакета бэкенд стартует, но методы стенда отвечают `503 stand_unavailable`, а страница показывает
ошибку с подсказкой собрать пакет. Очередь проверки и алиасы хранятся в памяти: перезапуск бэкенда их
сбрасывает.

## Как прогнать ступень выбора на decision-модели?

Ступень берёт кандидатов базлайна и спрашивает decision-модель, какое значение указано в карточке.
Без ключа работает офлайн-заглушка `lexical` — это проверка пайплайна, а не качество:

```bash
cd backend
uv run decide --provider lexical --splits val --sample 300
```

С ключом (переменные ниже, можно положить в `.env` в корне репозитория — команда его читает):

```bash
uv run decide --splits test,new_category --sample 8000 --mix-k 8 --dictionary \
  --override 0.0 --drop 0.6 --max-cost-usd 0.7 --concurrency 5 --name decision_jev
```

Пишет `reports/<name>.md|json` (сравнение с базлайном на той же выборке, калибровка, доля слотов в
модели, сетка порогов, стоимость) и `data/predictions/<name>.predictions.jsonl`. Ответы модели
кэшируются в `data/decision_cache/` по хешу запроса: повторный прогон с теми же настройками не платит.
`--max-cost-usd` останавливает платные вызовы, когда сумма `usage.cost` из ответов достигла лимита;
оставшиеся карточки получают значения базлайна.

## Какие переменные читает бэкенд?

Все необязательны: без них работает офлайн-реализация. `DECISION_MODEL_NAME` — идентификатор
модели в запросе: `jev-latest` у api.typesafe.ai (по умолчанию), `typesafe/jev-1.13` у OpenRouter
(`DECISION_MODEL_URL=https://openrouter.ai/api`).

| Переменная | По умолчанию | Что задаёт |
|---|---|---|
| `DECISION_MODEL` | `lexical` | `lexical` — офлайн-замена; `system_one` — HTTP-модель по контракту `/v1/systemone` |
| `DECISION_MODEL_URL` | `https://api.typesafe.ai` | Адрес модели для `system_one`, например локальный `laya-serve` |
| `DECISION_MODEL_API_KEY` | пусто | Ключ для `system_one`; без него заголовок `Authorization` не отправляется |
| `DECISION_MODEL_TIMEOUT_S` | `10` | Таймаут запроса к модели, секунды |
| `DECISION_MODEL_NAME` | `jev-latest` | Идентификатор модели в запросе; у OpenRouter — `typesafe/jev-1.13` |
| `LANGUAGE_MODEL` | `none` | `none`, `claude` или `codex` |
| `STAND_PACK` | `data/stand/pack.json.gz` | Путь к пакету данных стенда; в Compose — `/srv/data/stand/pack.json.gz` |
| `BACKEND_PORT` | `8000` | Порт бэкенда на хосте в Compose |
| `LLM` | `false` | Сборка: `true` ставит в образ SDK Claude и Codex |
| `TAG` | `latest` | Тег образов Compose и bake |

Неизвестное значение останавливает запуск с ошибкой, где названа переменная и допустимые значения.

## Как проверить фронтенд и презентацию?

Из корня, каждую команду отдельно:

```bash
(cd frontend && npm run verify)
(cd presentation && npm ci && npm run build)
```

## Как проверить бэкенд?

Нужен [uv](https://docs.astral.sh/uv/). Из корня:

```bash
cd backend
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest tests/unit
uv run pytest tests/integration
```

`tests/unit` работает без базы и сети; `tests/integration` требует локальную инфраструктуру
(PostgreSQL, запущенный стенд). `uv run pytest` запускает обе группы. Число процессов pytest-xdist
зависит от размера набора: маленький идёт в один процесс.

Тесты адаптера Claude подменяют вызов SDK и не ходят в сеть. Реальный вызов требует
`ANTHROPIC_API_KEY` или вход в Claude Code и расходует оплату.

## Что делать, если не запускается?

| Симптом | Что проверить |
|---|---|
| Порт 8080 занят | Задайте свободный `FRONTEND_PORT` в `.env` |
| Порт 8000 занят | Задайте свободный `BACKEND_PORT` в `.env` |
| Ошибка состояния API | `docker compose ps backend` и `docker compose logs backend`; затем `API_UPSTREAM` |
| `ConfigError` при старте бэкенда | Значение переменной из сообщения; допустимые перечислены там же |
| `LANGUAGE_MODEL=claude needs package` | Образ собран без SDK: пересоберите с `LLM=true` |
| `No such image` при `docker compose up` | Образы не собраны: `docker buildx bake` с теми же `COMPOSE_PROJECT_NAME` и `TAG` |
| Зависимости не скачиваются | Доступ к реестрам npm и Docker во время сборки |

---

<sub>[Оглавление документации](README.md) · [README проекта](../README.md)</sub>
