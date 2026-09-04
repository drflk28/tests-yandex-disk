import os
import uuid

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://cloud-api.yandex.net/v1/disk"
TOKEN = os.getenv("YANDEX_DISK_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "Не найден OAuth-токен. Добавьте его в переменную окружения "
        "YANDEX_DISK_TOKEN (см. README.md)."
    )


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def headers():
    return {
        "Authorization": f"OAuth {TOKEN}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session")
def session(headers):
    s = requests.Session()
    s.headers.update(headers)
    yield s
    s.close()


@pytest.fixture
def test_folder(session, base_url):
    """
    Создаёт уникальную тестовую папку перед тестом и гарантированно
    удаляет её после — тесты изолированы и не оставляют мусора на диске.
    """
    folder_name = f"/test_folder_{uuid.uuid4().hex[:8]}"
    resp = session.put(f"{base_url}/resources", params={"path": folder_name})
    assert resp.status_code == 201, f"Не удалось создать тестовую папку: {resp.text}"

    yield folder_name

    session.delete(
        f"{base_url}/resources",
        params={"path": folder_name, "permanently": "true"},
    )