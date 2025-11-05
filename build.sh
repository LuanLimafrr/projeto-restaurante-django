#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic (usando o caminho correto)
python projetorestaurante/projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações (usando o caminho correto)
python projetorestaurante/projetorestaurante/manage.py migrate --no-input

# 4. LIMPA o banco de dados de dados antigos
python projetorestaurante/projetorestaurante/manage.py flush --no-input

# 5. Carrega os dados (Assumindo que o JSON está ao lado do manage.py)
python projetorestaurante/projetorestaurante/manage.py loaddata projetorestaurante/projetorestaurante/initial_data.json