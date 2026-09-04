import pytest


@pytest.mark.smoke
class TestGet:
    def test_get_disk_info(self, session, base_url):
        """GET /v1/disk — получение общей информации о диске."""
        resp = session.get(base_url)

        assert resp.status_code == 200
        body = resp.json()
        assert "total_space" in body
        assert "used_space" in body
        assert body["total_space"] >= body["used_space"]

    def test_get_resource_metainfo(self, session, base_url, test_folder):
        """GET /v1/disk/resources — получение метаинформации о папке."""
        resp = session.get(f"{base_url}/resources", params={"path": test_folder})

        assert resp.status_code == 200
        body = resp.json()
        assert body["type"] == "dir"
        assert body["name"] == test_folder.lstrip("/")

    def test_get_resource_not_found(self, session, base_url):
        """GET несуществующего ресурса -> 404."""
        resp = session.get(
            f"{base_url}/resources",
            params={"path": "/no_such_resource_qwe123"},
        )

        assert resp.status_code == 404
        assert resp.json()["error"] == "DiskNotFoundError"

    def test_get_resources_flat_list(self, session, base_url):
        """GET /v1/disk/resources/files — плоский список файлов на диске."""
        resp = session.get(f"{base_url}/resources/files", params={"limit": 5})

        assert resp.status_code == 200
        assert "items" in resp.json()