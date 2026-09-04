import io


class TestPut:
    def test_create_folder(self, session, base_url):
        """PUT /v1/disk/resources — создание папки."""
        path = "/test_create_folder_case"
        try:
            resp = session.put(f"{base_url}/resources", params={"path": path})

            assert resp.status_code == 201
            assert resp.json()["href"].endswith(path.lstrip("/"))

            check = session.get(f"{base_url}/resources", params={"path": path})
            assert check.status_code == 200
            assert check.json()["type"] == "dir"
        finally:
            session.delete(
                f"{base_url}/resources",
                params={"path": path, "permanently": "true"},
            )

    def test_create_folder_conflict(self, session, base_url, test_folder):
        """Повторное создание уже существующей папки -> 409 Conflict."""
        resp = session.put(f"{base_url}/resources", params={"path": test_folder})

        assert resp.status_code == 409
        assert resp.json()["error"] == "DiskPathPointsToExistentDirectoryError"

    def test_upload_file(self, session, base_url, test_folder):
        """
        Загрузка файла — два шага:
        1) GET /v1/disk/resources/upload — получить одноразовую ссылку;
        2) PUT по этой ссылке — тело файла.
        """
        file_path = f"{test_folder}/sample.txt"

        link_resp = session.get(
            f"{base_url}/resources/upload",
            params={"path": file_path, "overwrite": "true"},
        )
        assert link_resp.status_code == 200
        upload_url = link_resp.json()["href"]

        upload_resp = session.put(upload_url, data=io.BytesIO(b"hello from autotests"))
        assert upload_resp.status_code in (201, 202)

        check = session.get(f"{base_url}/resources", params={"path": file_path})
        assert check.status_code == 200
        assert check.json()["type"] == "file"
        assert check.json()["size"] == len(b"hello from autotests")

    def test_upload_file_overwrite_false_conflict(self, session, base_url, test_folder):
        """Повторная загрузка того же файла без overwrite=true -> 409."""
        file_path = f"{test_folder}/duplicate.txt"

        first_link = session.get(
            f"{base_url}/resources/upload",
            params={"path": file_path, "overwrite": "false"},
        ).json()["href"]
        session.put(first_link, data=io.BytesIO(b"first version"))

        second_resp = session.get(
            f"{base_url}/resources/upload",
            params={"path": file_path, "overwrite": "false"},
        )
        assert second_resp.status_code == 409