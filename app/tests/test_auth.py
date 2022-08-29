from .override import client
import xmltodict

register_user_url = "/api/auth/register"
login_user_url = "/api/auth/login"
logout_user_url = "/api/auth/logout"

register_json_data = {
    "email": "tabish@gmail.com", 
    "username": "tabish", 
    "password": "12345678", 
    "password_confirm": "12345678"
}

register_xml_data = """
    <user>
        <email>tabish1@gmail.com</email>
        <username>tabish1</username>
        <password>12345678</password>
        <password_confirm>12345678</password_confirm>
    </user>
"""

login_json_data = {
    "email": "tabish@gmail.com",
    "password": "12345678"
}

login_xml_data = """
    <user>
        <email>tabish1@gmail.com</email>
        <password>12345678</password>
    </user>
"""

json_content_type = {'Content-Type': 'application/json'}
xml_content_type = {'Content-Type': 'application/xml'}

def test_create_user():
    response = client.post(register_user_url, json=register_json_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "tabish@gmail.com"
    assert "id" in data
    assert len(data) == 6

def test_create_xml_user():
    response = client.post(register_user_url, data=register_xml_data, headers=xml_content_type)

    assert response.status_code == 201
    data = xmltodict.parse(response.content)
    data = data['user']
    assert data["email"]['#text'] == "tabish1@gmail.com"
    assert "id" in data
    assert len(data) == 6

def test_login_user():
    response = client.post(login_user_url, json=login_json_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "access_token" in data

    cookies = response.cookies

    assert "access_token" in cookies
    assert "refresh_token" in cookies
    assert cookies['logged_in'] == 'True'

def test_login_xml_user():
    response = client.post(login_user_url, data=login_xml_data, headers=xml_content_type)

    assert response.status_code == 200
    data = xmltodict.parse(response.content)
    data = data['user']
    assert data["status"]['#text'] == "success"
    assert "access_token" in data

    cookies = response.cookies

    assert "access_token" in cookies
    assert "refresh_token" in cookies
    assert cookies['logged_in'] == 'True'

def test_logout_user():
    response = client.get(logout_user_url, headers=json_content_type)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["email"] == "tabish@gmail.com"

def test_logout_xml_user():
    response = client.get(logout_user_url, headers=xml_content_type)
    assert response.status_code == 200
    data = xmltodict.parse(response.content)
    data = data['user']
    assert data["status"]["#text"] == "success"
    assert data["email"]["#text"] == "tabish@gmail.com"
