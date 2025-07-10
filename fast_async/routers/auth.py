from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_async.database import get_session
from fast_async.models import User
from fast_async.schemas import Token
from fast_async.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
async def login_for_access_token(
    session: T_Session,
    form_data: OAuth2Form,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or username',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or username',
        )
    data = {'sub': user.email}

    token_access = create_access_token(data)

    return {'token_access': token_access, 'token_type': 'Bearer'}


@router.post('/refresh-token', status_code=HTTPStatus.OK, response_model=Token)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'token_access': new_access_token, 'token_type': 'Bearer'}
