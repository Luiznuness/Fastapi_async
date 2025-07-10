from http import HTTPStatus


def test_app_verificar_retorno(client):
    resultado = client.get('/')

    assert resultado.status_code == HTTPStatus.OK
    assert resultado.json() == {'message': 'Olá Mundo!'}
