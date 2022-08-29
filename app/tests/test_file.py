import os
from .override import client
import xmltodict

path = os.path.abspath(os.path.join("test_file.jpeg"))
file = ("test_file.jpeg", open(path, "rb").read(), "image/jpeg")

upload_image_url = "/api/file/upload"

def test_upload_image():
    response = client.post(
        upload_image_url,
        files={"file": file},
        headers={"Accept": "application/json", }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "url" in data

    global get_file_url
    get_file_url = data['url']

def test_upload_image_xml():
    response = client.post(
        upload_image_url,
        files={"file": file},
        headers={"Accept": "application/xml"}
    )
    
    assert response.status_code == 201
    data = xmltodict.parse(response.content)
    data = data["file"]
    assert data["status"]["#text"] == "success"
    assert "url" in data

def test_get_file():
    response = client.get(
        get_file_url,
    )

    response.status_code == 200
    data = response.content

    with open(path, "rb") as f:
        assert f.read() == data


