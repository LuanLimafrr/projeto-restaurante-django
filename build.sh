#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic (Caminho correto)
python projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações (Caminho correto)
python projetorestaurante/manage.py migrate --no-input

# 4. LIMPA o banco de dados de dados antigos (Resolve o erro "duplicate key")
python projetorestaurante/manage.py flush --no-input

# 5. Carrega os dados (O manage.py e o initial_data.json estão na mesma pasta)
python projetorestaurante/manage.py loaddata projetorestaurante/initial_data.json