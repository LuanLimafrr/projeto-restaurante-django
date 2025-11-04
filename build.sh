#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic (usando o caminho correto)
python projetorestaurante/projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações (usando o caminho correto)
python projetorestaurante/projetorestaurante/manage.py migrate --no-input

# 4. Carrega os dados (o initial_data.json deve estar na mesma pasta do manage.py)
python projetorestaurante/projetorestaurante/manage.py loaddata initial_data.json