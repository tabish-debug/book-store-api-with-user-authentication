from .override import client
import xmltodict

current_user_url = "/api/user/me"

json_content_type = {'Content-Type': 'application/json'}
xml_content_type = {'Content-Type': 'application/xml'}

def test_user_me():
    response = client.get(current_user_url, headers=json_content_type)

    assert response.status_code == 200
    data = response.json()
    assert data['email'] == 'tabish@gmail.com'
    assert data['username'] == 'tabish'

def test_user_xml_me():
    response = client.get(current_user_url, headers=xml_content_type)

    assert response.status_code == 200
    data = xmltodict.parse(response.content)
    data = data['user']
    assert data['email']['#text'] == 'tabish@gmail.com'
    assert data['username']['#text'] == 'tabish'
