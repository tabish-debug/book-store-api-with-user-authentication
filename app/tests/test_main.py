from .override import client

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "server is running"}