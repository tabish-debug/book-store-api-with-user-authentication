from .override import client
import xmltodict

books_url = "/api/store/books"

create_json_data = {
    "title": "This is my book",
    "description": "This is my book description",
    "price": 1001.20
}

create_xml_data = """
    <book>
        <title>This is xml book</title>
        <description>This is xml book description</description>
        <price>100.20</price>
    </book>
"""

update_json_data = {
    'title': 'This is updated book',
    'price': 2003.33
}

update_xml_data = """
    <book>
        <title>This is xml updated book</title>
        <price>1012.20</price>
    </book>
"""

pagination_params = { 'page': 1, 'per_page': 1 }

def test_create_book():
    response = client.post(books_url, json=create_json_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["cover_image"] == "None"

def test_create_xml_book():
    response = client.post(books_url, data=create_xml_data,
        headers={'Content-Type': 'application/xml'} 
    )

    assert response.status_code == 201
    data = xmltodict.parse(response.content)
    data = data['book']
    assert 'id' in data
    assert data['cover_image']['#text'] == 'None'
    assert data['title']['#text'] == 'This is xml book'
    
def test_get_all_books():
    response = client.get(books_url, params=pagination_params,
        headers={'Content-Type': 'application/json'}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["rows"]) == 1
    assert data["summary"]["total"] == 2
    assert data["summary"]["total_pages"] == 2

def test_get_all_xml_books():
    response = client.get(books_url, params=pagination_params,
        headers={'Content-Type': 'application/xml'}
    )

    assert response.status_code == 200
    data = xmltodict.parse(response.content)
    data = data['books']
    assert int(data["summary"]["per_page"]['#text']) == 1
    assert int(data["summary"]["total"]['#text']) == 2
    assert int(data["summary"]["total_pages"]['#text']) == 2

def test_search_all_books():
    search_param = {"search": "description"}
    response = client.get(books_url, params={**search_param, **pagination_params},
        headers={'Content-Type': 'application/json'}
    )

    assert response.status_code == 200
    data = response.json()
    for row in data["rows"]:
        assert search_param['search'] in row["description"] or search_param['search'] in row['title']
    assert len(data["rows"]) == 1
    assert data["summary"]["total"] == 2
    assert data["summary"]["total_pages"] == 2

def test_get_all_books_of_user():
    response = client.get(f"{books_url}/user", params=pagination_params,
        headers={'Content-Type': 'application/json'}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["rows"]) == 1
    assert data["summary"]["total"] == 2
    assert data["summary"]["total_pages"] == 2

def test_get_single_book():
    response = client.get(f"{books_url}/{1}", headers={'Content-Type': 'application/json'})

    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'This is my book'
    assert float(data['price']) == 1001.20

def test_get_single_xml_book():
    response = client.get(f"{books_url}/{1}", headers={'Content-Type': 'application/xml'})

    assert response.status_code == 200
    data = xmltodict.parse(response.content)
    data = data['book']
    assert data['title']['#text'] == 'This is my book'
    assert float(data['price']['#text']) == 1001.20

def test_update_book():
    response = client.put(f"{books_url}/{1}", json=update_json_data,
    )

    assert response.status_code == 205
    data = response.json()
    assert data['detail'] == 'book updated successfully'

    response = client.get(
        f"/api/store/books/{1}",
        headers={'Content-Type': 'application/json'}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'This is updated book'
    assert float(data['price']) == 2003.33

def test_update_xml_book():
    response = client.put(
        f"/api/store/books/{2}",
        data=update_xml_data,
        headers={'Content-Type': 'application/xml'}
    )

    assert response.status_code == 205
    data = xmltodict.parse(response.content)
    data = data['book']
    assert data['detail']['#text'] == 'book updated successfully'

    response = client.get(f"{books_url}/{2}", headers={'Content-Type': 'application/xml'})

    assert response.status_code == 200
    data = xmltodict.parse(response.content)
    data = data['book']
    assert data['title']['#text'] == 'This is xml updated book'
    assert float(data['price']['#text']) == 1012.20

def test_delete_book():
    response = client.delete(f"{books_url}/{1}", headers={"Content-Type": "application/json"})

    assert response.status_code == 204
    data = response.json()
    assert data['detail'] == "book deleted successfully"   

def test_delete_xml_book():
    response = client.delete(f"{books_url}/{2}", headers={"Content-Type": "application/xml"})

    assert response.status_code == 204
    data = xmltodict.parse(response.content)
    assert data['book']['detail']['#text'] == "book deleted successfully"   
