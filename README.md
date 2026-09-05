# tests-yandex-disk

Автотесты для REST API Яндекс.Диска (`https://cloud-api.yandex.net`).

Стек: **Python 3, Pytest, requests**. Дополнительно: `python-dotenv` — хранение
токена вне кода.

Покрыты все четыре HTTP-метода:

| Метод  | Эндпоинт                                | Файл теста           |
|--------|-------------------------------------------|------------------------|
| GET    | `/v1/disk`, `/v1/disk/resources`          | `tests/test_get.py`   |
| PUT    | `/v1/disk/resources`, upload по ссылке    | `tests/test_put.py`   |
| POST   | `/v1/disk/resources/copy`                 | `tests/test_post.py`  |
| DELETE | `/v1/disk/resources`, `/trash/resources`  | `tests/test_delete.py`|

Для каждого метода есть позитивный сценарий и негативные (404/409).


## Подготовка к запуску

### 1. Клонировать репозиторий

```bash
git clone <ссылка на репозиторий>
cd tests-yandex-disk
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Получить OAuth-токен Яндекс.Диска

**Не используйте личный аккаунт** — заведите отдельный технический аккаунт.

Самый быстрый способ — через [полигон](https://yandex.ru/dev/disk/poligon/):
получить временный токен для проверки запросов.

Для постоянного использования — зарегистрировать приложение на
[oauth.yandex.ru](https://oauth.yandex.ru/) с правами:
`cloud_api:disk.read`, `cloud_api:disk.write`, `cloud_api:disk.info`.

### 4. Указать токен

В корне проекта создать файл `.env`:

YANDEX_DISK_TOKEN=вставьте_сюда_токен


## Запуск тестов

```bash
python -m pytest            # все тесты
python -m pytest -v         # подробный вывод
python -m pytest tests/test_get.py     # только один файл
python -m pytest -m smoke   # быстрый smoke-набор
```

> На Windows, если `pytest` как отдельная команда блокируется политикой
> безопасности (`ApplicationFailedException` / Smart App Control), запускайте
> через интерпретатор: `python -m pytest`.
