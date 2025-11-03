#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala as dependências do requirements.txt (que você moveu para a raiz)
pip install -r requirements.txt

# Garante que as pastas MEDIA_ROOT e STATIC_ROOT existam antes de serem usadas
# 'mkdir -p' cria a pasta se ela não existe, sem erro se já existe.
mkdir -p projetorestaurante/restaurante/media
mkdir -p staticfiles_coletados

# Roda o collectstatic, que agora vai copiar também os arquivos de MEDIA_ROOT para STATIC_ROOT
python projetorestaurante/manage.py collectstatic --no-input

# Roda as migrações do banco de dados
python projetorestaurante/manage.py migrate

