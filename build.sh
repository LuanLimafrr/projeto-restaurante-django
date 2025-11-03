#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic
# (Apontando para a pasta correta do manage.py)
python projetorestaurante/projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações
# (Apontando para a pasta correta do manage.py)
python projetorestaurante/projetorestaurante/manage.py migrate --no-input

# 4. Carrega os dados
# (O loaddata usa o manage.py como referência para encontrar o initial_data.json)
python projetorestaurante/projetorestaurante/manage.py loaddata initial_data.json