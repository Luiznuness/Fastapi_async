from datetime import datetime, timedelta
from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    resultado = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    token = resultado.json()

    assert resultado.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'token_access' in token


def test_get_token_user_error(client):
    resultado = client.post(
        '/auth/token',
        data={
            'username': 'test@test.com',
            'password': 'test',
        },
    )

    assert resultado.status_code == HTTPStatus.UNAUTHORIZED
    assert resultado.json() == {'detail': 'Incorrect email or username'}


def test_get_token_password_error(client, user):
    resultado = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'Luiz',
        },
    )

    assert resultado.status_code == HTTPStatus.UNAUTHORIZED
    assert resultado.json() == {'detail': 'Incorrect email or username'}


def test_token_expired_after_time_error(client, user):
    with freeze_time(datetime.now()):
        response = client.post(
            'auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        assert 'token_access' in response.json()
        token = response.json()['token_access']

    with freeze_time(datetime.now() + timedelta(minutes=30)):
        response = client.put(
            f'/users/{user.id}',
            json={
                'username': 'alice',
                'email': 'alice@test.com',
                'password': 'teste',
            },
            headers={'authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_access_token(client, token):
    response = client.post(
        'auth/refresh-token',
        headers={'authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'token_access' in response.json()
    assert 'token_type' in response.json()
    assert response.json()['token_type'] == 'Bearer'


def test_token_expired_after_time_refresh(client, user):
    with freeze_time(datetime.now()):
        response = client.post(
            'auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        assert 'token_access' in response.json()
        token = response.json()['token_access']

    with freeze_time(datetime.now() + timedelta(minutes=30)):
        response = client.post(
            'auth/refresh-token',
            headers={'authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
