import pytest
from app import app

@pytest.fixture
def client():
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

def test_pagar_exitoso(client):
    response = client.get('/billetera/pagar?minumero=123456789&numerodestino=123456787&valor=100')
    assert response.status_code == 200
    assert response.get_json().get('success') == True

def test_pagar_fallo_406(client):
    response = client.get('/billetera/pagar?minumero=123456789&numerodestino=123456789&valor=100')
    assert response.status_code == 406

def test_pagar_fallo_422(client):
    response = client.get('/billetera/pagar?minumero=')
    assert response.status_code == 422

def test_historial_exitoso(client):
    response = client.get('/billetera/historial?minumero=123456789')
    assert response.status_code == 200
    assert 'datos' in response.get_json()

