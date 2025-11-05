#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências
pip install -r requirements.txt

# 2. Roda o collectstatic
python projetorestaurante/projetorestaurante/manage.py collectstatic --no-input

# 3. Roda as migrações (Cria/Atualiza as tabelas)
# ESTE É O ÚNICO COMANDO DE DADOS QUE DEVE RODAR SEMPRE
python projetorestaurante/projetorestaurante/manage.py migrate --no-input

# 4. LINHA 'FLUSH' REMOVIDA (NÃO VAMOS MAIS APAGAR O BANCO)
# 5. LINHA 'LOADDATA' REMOVIDA (OS DADOS JÁ ESTÃO LÁ)
# 6. LINHA 'CREATESUPERUSER' REMOVIDA (O SUPERUSER JÁ ESTÁ LÁ)

# Se você precisar criar o superusuário de novo (ex: se apagar o DB no Render), 
# descomente a linha abaixo TEMPORARIAMENTE para UM deploy:
# python projetorestaurante/projetorestaurante/manage.py createsuperuser --noinput