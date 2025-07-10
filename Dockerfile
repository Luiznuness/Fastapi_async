FROM python:3.13-slim
# Não cria um ambiente virtual (poetry) no container
ENV POETRY_VISTUALENVS_CREATE=false

WORKDIR app/
COPY . .

RUN pip install poetry
# Configura o Poetry para usar até 10 workers para 
# instalar as dependências do projeto
RUN poetry config installer.max-workers 10 
# Instala as dependências listadas no pyproject.toml, 
# sem pedir interações, sem caracteres de formatação 
# de terminal, e ignorando os pacotes do grupo dev
RUN poetry install --no-interaction --no-ansi --without dev

EXPOSE 8000

CMD poetry run uvicorn --host 0.0.0.0 fast_async.app:app