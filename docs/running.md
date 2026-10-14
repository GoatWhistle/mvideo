# Запуск и проверки

Compose запускает экран заполнения и потоковый API. Без ключа работают правила; при настройке
Jev спорные кандидаты проверяются автоматически. SQLite сохраняет каталог, исправления и алиасы.

**Читайте, если** вы запускаете стенд · **Связано:** [архитектура](architecture.md) · [зависимости](dependencies.md)

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
mkdir -p data
dbmate --url sqlite:data/app.db --migrations-dir migrations/sqlite --no-dump-schema up
uv run seed-catalog --database data/app.db
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
`new_category` и пишет (`--splits val` — тот же прогон на настроечном сплите, отчёт `reports/baseline_v2_val.md`):

| Файл | Что внутри |
|---|---|
| `data/predictions/baseline_v2.predictions.jsonl` | По строке на карточку: `sku_id`, `category_id`, `split`, `confidence_calibrated: false`, `attributes: {атрибут: {value, confidence, source, sources, evidence, start, end}}` — значения с уверенностью от 0,35; `review` — то же для значений ниже порога, очередь проверки |
| `data/predictions/baseline_v2.candidates.parquet` | Все кандидаты для следующих ступеней: `sku_id`, `attribute`, `key`, `value`, `evidence`, `start`, `end`, `source`, `zone`, `affinity`, `prior`, `seller_fit`, `slot`, `score`, `chosen` |
| `reports/baseline_v2.md`, `reports/baseline_v2.json` | Метрики по [плану валидации](validation-plan.md): сводка по срезам и таблицы по атрибутам |

Предсказания для всех 1,18 млн карточек с текстом, без оценки:

```bash
uv run baseline --data ../data/processed --out ../data/predictions --all-cards --no-candidates
```

Пишет `data/predictions/baseline_v2_all.predictions.jsonl`. У карточек вне каталога категории нет, для
них извлекаются только бренд и цвет.

## Какие переменные читает бэкенд?

Все необязательны: без них работает офлайн-реализация после миграций и seed.

| Переменная | По умолчанию | Что задаёт |
|---|---|---|
| `DATABASE_PATH` | `data/app.db` локально, `/data/app.db` в Compose | Файл SQLite, подготовленный миграциями и seed |
| `DECISION_MODEL` | `lexical` | `lexical` — офлайн-замена; `system_one` — HTTP-модель по контракту `/v1/systemone` |
| `DECISION_MODEL_URL` | `https://api.typesafe.ai` | Адрес модели для `system_one`, например локальный `laya-serve` |
| `DECISION_MODEL_API_KEY` | пусто | Ключ для `system_one`; без него заголовок `Authorization` не отправляется |
| `DECISION_MODEL_TIMEOUT_S` | `10` | Таймаут запроса к модели, секунды |
| `LANGUAGE_MODEL` | `none` | `none`, `claude` или `codex` |
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
DBMATE_BIN=dbmate TEST_API_URL=http://localhost:8000 uv run pytest tests/integration
```

`tests/unit` работает без базы и сети; `tests/integration` требует dbmate 2.36.0 в PATH
(или `DBMATE_BIN` с путём к бинарнику) и запущенный стенд в режиме правил (`TEST_API_URL`).
SQLite-тесты применяют миграции к временным файлам, без отдельного сервера. `uv run pytest` запускает обе группы. Число процессов pytest-xdist
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

## Как проверить автоматическое заполнение?

Откройте интерфейс, вставьте текст и нажмите «Заполнить карточку»:

```text
Смартфон Samsung Galaxy S26 12/256GB Black
Вес: 500 г
```

Без ключа ожидаются категория «Смартфоны», 12 ГБ RAM, 256 ГБ ROM, вес 0.5 кг,
бренд, модель и цвет с цитатами. Нажатие на цитату показывает её в исходнике.
«Скачать JSON» выгружает заполненные поля отдельно от исключений.

Seed по умолчанию загружает `backend/src/app/assets/demo-catalog.json` в SQLite. Для нового
локального хранилища с другим каталогом выполните после миграций:

```bash
uv run seed-catalog --database data/custom.db --catalog /absolute/path/catalog.json
```

Затем задайте
`DATABASE_PATH=data/custom.db`. Seed не перезаписывает уже существующий каталог.

В Compose цепочка `storage-init → migrate → seed → backend` выполняется автоматически.
Именованный том `catalog-data` сохраняет данные при перезапуске и `docker compose down`;
`docker compose down -v` удаляет данные. Проверка повторного seed: `docker compose run --rm seed`.
Для локальной разработки dbmate устанавливается отдельно из официального релиза 2.36.0.

Для Jev задайте `DECISION_MODEL=system_one` и `DECISION_MODEL_API_KEY` в локальном окружении.
`DECISION_MODEL_TIMEOUT_S` задаёт общий бюджет этапа, максимум два обращения.
Для собственного сервиса можно задать `DECISION_MODEL_URL`; ключ зависит от сервиса.
Запрос к TypeSafe без ключа не выполняется, остаётся режим правил. Платный прогон запускается отдельно.

## Как запустить аудит данных?

Из корня репозитория:

```bash
cd backend
uv run audit-catalog --data ../data/processed --revision "$(git rev-parse HEAD)" --out ../reports/catalog-audit.json
```

Команда требует подготовленные parquet-файлы, не обращается к моделям и не перезаписывает отчёт.
Метод группирования и ограничения описаны в [автоматическом заполнении](automatic-catalog.md).
Новые baseline-прогоны пишутся под именами `baseline_v2*`; старые отчёты не заменяются.

Для интеграционной проверки уже запущенного backend в режиме `DECISION_MODEL=lexical`:

```bash
cd backend
DBMATE_BIN=dbmate TEST_API_URL=http://localhost:8000 uv run pytest tests/integration
```

Браузерный сценарий проверяет реальные API-ответы и экспорт, без подмены результатов:

```bash
cd frontend
npx playwright install chromium --only-shell
E2E_BASE_URL=http://localhost:8080 npm run e2e
```
