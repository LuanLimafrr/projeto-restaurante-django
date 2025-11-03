#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic (Caminho correto)
python projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações (Caminho correto)
python projetorestaurante/manage.py migrate --no-input

# 4. Carrega os dados (Caminho correto)
# O manage.py está em 'projetorestaurante/', e o .json também, então ele o encontrará.
python projetorestaurante/manage.py loaddata initial_data.json