import io


class TestPost:
    def test_copy_resource(self, session, base_url, test_folder):
        """POST /v1/disk/resources/copy — копирование файла внутри диска."""
        source = f"{test_folder}/source.txt"
        destination = f"{test_folder}/copy.txt"

        upload_link = session.get(
            f"{base_url}/resources/upload",
            params={"path": source, "overwrite": "true"},
        ).json()["href"]
        session.put(upload_link, data=io.BytesIO(b"content to copy"))

        resp = session.post(
            f"{base_url}/resources/copy",
            params={"from": source, "path": destination},
        )
        assert resp.status_code == 201

        check = session.get(f"{base_url}/resources", params={"path": destination})
        assert check.status_code == 200
        assert check.json()["type"] == "file"

    def test_copy_resource_not_found(self, session, base_url, test_folder):
        """Копирование несуществующего исходного файла -> 404."""
        resp = session.post(
            f"{base_url}/resources/copy",
            params={
                "from": f"{test_folder}/no_such_file.txt",
                "path": f"{test_folder}/copy.txt",
            },
        )

        assert resp.status_code == 404
        assert resp.json()["error"] == "DiskNotFoundError"

    def test_copy_resource_conflict(self, session, base_url, test_folder):
        """Копирование в уже занятый путь без overwrite -> 409."""
        source = f"{test_folder}/source2.txt"
        destination = f"{test_folder}/existing.txt"

        for path in (source, destination):
            link = session.get(
                f"{base_url}/resources/upload",
                params={"path": path, "overwrite": "true"},
            ).json()["href"]
            session.put(link, data=io.BytesIO(b"data"))

        resp = session.post(
            f"{base_url}/resources/copy",
            params={"from": source, "path": destination, "overwrite": "false"},
        )
        assert resp.status_code == 409