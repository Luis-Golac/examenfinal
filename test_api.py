import pytest
from myapp import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

def test_contactos_exitoso(client):
    response = client.get('/billetera/contactos?minumero=123456789')
    assert response.status_code == 200
    assert 'contactos' in response.get_json()

def test_contactos_fallo_422(client):
    response = client.get('/billetera/contactos')
    assert response.status_code == 422

