from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_async.models import User


@pytest.mark.asyncio
async def test_add_db(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        dados_user = User(
            username='Luiz', email='luiz@test.com', password='LuizTeste'
        )

        session.add(dados_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'Luiz')
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'Luiz',
        'email': 'luiz@test.com',
        'password': 'LuizTeste',
        'created_at': time,
        'updated_at': time,
        'todos': [],
    }
