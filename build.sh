#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic
python projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações
python projetorestaurante/manage.py migrate --no-input

# 4. Carrega os dados
python projetorestaurante/manage.py loaddata initial_data.json