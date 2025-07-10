from http import HTTPStatus

from fast_async.schemas import UserPublic


def test_created_user(client):
    resultado = client.post(
        '/users',
        json={
            'username': 'Luiz',
            'email': 'luiz@gmail.com',
            'password': 'Luiz',
        },
    )

    assert resultado.status_code == HTTPStatus.CREATED
    assert resultado.json() == {
        'username': 'Luiz',
        'email': 'luiz@gmail.com',
        'id': 1,
    }


def test_created_integrity_error_username(client, user):
    resultado = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'luiz@test.com',
            'password': 'test',
        },
    )

    assert resultado.status_code == HTTPStatus.CONFLICT
    assert resultado.json() == {'detail': 'Username already exists'}


def test_created_integrity_error_email(client, user):
    resultado = client.post(
        '/users/',
        json={
            'username': 'luiz',
            'email': user.email,
            'password': 'test',
        },
    )

    assert resultado.status_code == HTTPStatus.CONFLICT
    assert resultado.json() == {'detail': 'Email already exists'}


def test_read_user(client, user, token):
    model_user = UserPublic.model_validate(user).model_dump()

    resultado = client.get(
        '/users/', headers={'authorization': f'Bearer {token}'}
    )

    assert resultado.status_code == HTTPStatus.OK
    assert resultado.json() == {'users': [model_user]}


def test_update_user(client, token):
    resultado = client.put(
        '/users/1',
        json={
            'username': 'Luiz',
            'email': 'luiz@gmail.com',
            'password': 'Luiz',
        },
        headers={'authorization': f'Bearer {token}'},
    )

    assert resultado.status_code == HTTPStatus.OK
    assert resultado.json() == {
        'username': 'Luiz',
        'email': 'luiz@gmail.com',
        'id': 1,
    }


def test_delete_user(client, token):
    resultado = client.delete(
        '/users/1', headers={'authorization': f'Bearer {token}'}
    )

    assert resultado.status_code == HTTPStatus.OK
    assert resultado.json() == {'message': 'User deleted'}


def test_read_user_id(client, user, token):
    user_model = UserPublic.model_validate(user).model_dump()

    resultado = client.get(
        '/users/1',
        headers={'authorization': f'Bearer {token}'},
    )

    assert resultado.status_code == HTTPStatus.OK
    assert resultado.json() == user_model


def test_error_read_user(client, token):
    resultado = client.get(
        '/users/2',
        headers={'authorization': f'Bearer {token}'},
    )

    assert resultado.status_code == HTTPStatus.NOT_FOUND
    assert resultado.json() == {'detail': 'User not found'}


def test_update_integrity_error(client, token, other_user):
    resultado = client.put(
        '/users/1',
        json={
            'username': 'Luiz',
            'email': other_user.email,
            'password': 'teste',
        },
        headers={'authorization': f'Bearer {token}'},
    )

    assert resultado.status_code == HTTPStatus.CONFLICT
    assert resultado.json() == {'detail': 'Username or Email already exists'}


def test_update_error_permissons(client, token, other_user):
    resultado = client.put(
        f'/users/{other_user.id}',
        json={
            'username': 'alice',
            'email': 'alice@test.com',
            'password': 'teste',
        },
        headers={'authorization': f'Bearer {token}'},
    )

    assert resultado.status_code == HTTPStatus.FORBIDDEN
    assert resultado.json() == {'detail': 'Not enough permissions'}


def test_delete_error_permissons(client, token, other_user):
    resultado = client.delete(
        f'/users/{other_user.id}',
        headers={'authorization': f'Bearer {token}'},
    )

    assert resultado.status_code == HTTPStatus.FORBIDDEN
    assert resultado.json() == {'detail': 'Not enough permissions'}
