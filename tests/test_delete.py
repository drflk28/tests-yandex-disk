import time
import uuid


def wait_for_operation(session, operation_href, timeout=15, interval=1):
    """Опрашивает статус асинхронной операции, пока она не завершится."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = session.get(operation_href)
        status = resp.json().get("status")
        if status in ("success", "failed"):
            return status
        time.sleep(interval)
    raise TimeoutError("Операция не завершилась за отведённое время")


def wait_for_status(get_request, expected_status, timeout=10, interval=1):
    """Повторяет запрос, пока не получит ожидаемый код ответа, либо не истечёт таймаут."""
    deadline = time.time() + timeout
    resp = None
    while time.time() < deadline:
        resp = get_request()
        if resp.status_code == expected_status:
            return resp
        time.sleep(interval)
    return resp


class TestDelete:
    def test_delete_folder_permanently(self, session, base_url):
        """DELETE /v1/disk/resources — безвозвратное удаление ресурса."""
        path = f"/test_delete_folder_{uuid.uuid4().hex[:8]}"
        session.put(f"{base_url}/resources", params={"path": path})

        resp = session.delete(
            f"{base_url}/resources",
            params={"path": path, "permanently": "true"},
        )
        assert resp.status_code in (202, 204)

        if resp.status_code == 202:
            assert wait_for_operation(session, resp.json()["href"]) == "success"

        check = wait_for_status(
            lambda: session.get(f"{base_url}/resources", params={"path": path}),
            expected_status=404,
        )
        assert check.status_code == 404

    def test_delete_moves_to_trash_by_default(self, session, base_url):
        """DELETE без permanently=true перемещает ресурс в корзину."""
        path = f"/test_delete_to_trash_{uuid.uuid4().hex[:8]}"
        session.put(f"{base_url}/resources", params={"path": path})

        resp = session.delete(f"{base_url}/resources", params={"path": path})
        assert resp.status_code in (202, 204)

        if resp.status_code == 202:
            assert wait_for_operation(session, resp.json()["href"]) == "success"

        expected_origin = f"disk:{path}"

        def find_in_trash():
            listing = session.get(
                f"{base_url}/trash/resources", params={"path": "/", "limit": 100}
            )
            items = listing.json().get("_embedded", {}).get("items", [])
            return next((i for i in items if i["origin_path"] == expected_origin), None)

        deadline = time.time() + 10
        trashed_item = None
        while time.time() < deadline:
            trashed_item = find_in_trash()
            if trashed_item:
                break
            time.sleep(1)

        assert trashed_item is not None, "Ресурс не найден в корзине по origin_path"

        # удаляем именно этот элемент из корзины
        session.delete(f"{base_url}/trash/resources", params={"path": trashed_item["path"].replace("trash:", "", 1)})

    def test_delete_nonexistent_resource(self, session, base_url):
        """Удаление несуществующего ресурса -> 404."""
        resp = session.delete(
            f"{base_url}/resources",
            params={"path": "/no_such_resource_qwe123", "permanently": "true"},
        )

        assert resp.status_code == 404
        assert resp.json()["error"] == "DiskNotFoundError"