#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic
# (Isso vai coletar o CSS/JS E as imagens que você moveu para 'static/')
python projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações (Cria as tabelas vazias no banco de dados do Render)
python projetorestaurante/manage.py migrate --no-input

# 4. Carrega os dados (CORREÇÃO APLICADA AQUI)
python projetorestaurante/manage.py loaddata initial_data.json