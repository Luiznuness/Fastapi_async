from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from fast_async.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test todo',
                'description': 'Test todo description',
                'state': 'draft',
            },
        )

    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, token, user, client):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get(
        '/todos/',
        headers={'authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_offset_limit(session, token, user, client):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title(session, token, user, client):
    expected_todos = 2
    test_title = 'test title'
    session.add_all(
        TodoFactory.create_batch(2, user_id=user.id, title=test_title)
    )

    await session.commit()

    response = client.get(
        f'/todos/?title={test_title}',
        headers={'authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description(session, token, user, client):
    expected_todos = 2
    test_description = 'test description'
    session.add_all(
        TodoFactory.create_batch(
            2,
            user_id=user.id,
            description=test_description,
        )
    )

    await session.commit()

    response = client.get(
        f'/todos/?description={test_description}',
        headers={'authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state(session, token, user, client):
    expected_todos = 2
    session.add_all(
        TodoFactory.create_batch(2, user_id=user.id, state=TodoState.todo)
    )

    await session.commit()

    response = client.get(
        '/todos/?state=todo',
        headers={'authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_delete_todo(client, session, user, token):
    session.add(TodoFactory(user_id=user.id))

    await session.commit()

    response = client.delete(
        '/todos/1',
        headers={'authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


def test_delete_todos_error_todo_not_found(client, token):
    response = client.delete(
        '/todos/1',
        headers={'authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_patch_todo(client, session, user, token):
    session.add(TodoFactory(user_id=user.id))

    await session.commit()

    response = client.patch(
        '/todos/1',
        json={'title': 'Test Title!'},
        headers={'authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'Test Title!'


def test_patch_todo_error_user_not_found(client, token):
    response = client.patch(
        '/todos/1',
        json={'title': 'Test Title!'},
        headers={'authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_get_todos_all_values(
    client, session, token, user, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory(user_id=user.id)

        session.add(todo)
        await session.commit()

    response = client.get(
        '/todos/',
        headers={'authorization': f'Bearer {token}'},
    )

    assert response.json()['todos'] == [
        {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'state': todo.state,
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
        }
    ]


def test_list_todos_filter_title_min(token, client):
    test_title = 'l'

    response = client.get(
        f'/todos/?title={test_title}',
        headers={'authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_list_todos_filter_title_max(token, client):
    test_title = 'l' * 23

    response = client.get(
        f'/todos/?title={test_title}',
        headers={'authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
