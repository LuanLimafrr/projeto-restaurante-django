#!/usr/bin/env bash
# exit on error
set -o errexit

# CORRIGIDO: Agora lê o requirements.txt da pasta raiz (onde ele está agora)
pip install -r requirements.txt

# Os comandos do manage.py AINDA estão na subpasta 'projetorestaurante'
python projetorestaurante/manage.py collectstatic --no-input
python projetorestaurante/manage.py migrate

