#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala dependências (o requirements.txt está na subpasta)
pip install -r projetorestaurante/requirements.txt

# Roda os comandos (o manage.py está na subpasta)
python projetorestaurante/manage.py collectstatic --no-input
python projetorestaurante/manage.py migrate