#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic
python projetorestaurante/projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações (Cria as tabelas)
python projetorestaurante/projetorestaurante/manage.py migrate --no-input

# 4. LIMPA o banco de dados
python projetorestaurante/projetorestaurante/manage.py flush --no-input

# 5. Carrega os dados do Cardápio
python projetorestaurante/projetorestaurante/manage.py loaddata projetorestaurante/projetorestaurante/initial_data.json

# 6. CRIA O SUPERUSUÁRIO (ESTE É O COMANDO QUE FALTAVA)
# (Usa as variáveis que você configurou no Render)
python projetorestaurante/projetorestaurante/manage.py createsuperuser --noinput