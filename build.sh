#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic (Caminho correto)
python projetorestaurante/projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações (Caminho correto)
python projetorestaurante/projetorestaurante/manage.py migrate --no-input

# 4. Carrega os dados (CORREÇÃO AQUI: Fornecendo o caminho completo)
python projetorestaurante/projetorestaurante/manage.py loaddata projetorestaurante/projetorestaurante/initial_data.json