


async def test_list_alerts_view(client):
    response = await client.get("/alerts")
    assert response.status_code == 200


async def test_list_files_view(client):
    response = await client.get("/files")
    assert response.status_code == 200


async def test_create_file_view(client):
    data = {"title": "test_title"}
    files = {
        "file": ("test_filename.txt", b"test_content", "text/plain")
    }

    response = await client.post("/files", data=data, files=files)
    assert response.status_code == 201


async def test_get_files_view(client):
    file_id = 1
    response = await client.get(f"/files/{file_id}")
    print(response.json())
    assert response.status_code == 200


async def test_update_file_view(client):
    file_id = 1
    data = {"title": "test_title"}

    response = await client.patch(f"/files/{file_id}", json=data)
    print(response.json())
    assert response.status_code == 200


async def test_download_file(client):
    file_id = 1
    response = await client.get(f"/files/{file_id}/download")
    assert response.status_code == 200


async def test_delete_file_view(client):
    file_id = 1
    response = await client.delete(f"/files/{file_id}")
    assert response.status_code == 204