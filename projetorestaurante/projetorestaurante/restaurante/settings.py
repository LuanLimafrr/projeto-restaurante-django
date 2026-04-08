# /projetorestaurante/restaurante/settings.py
# VERSÃO CORRIGIDA PARA PRODUÇÃO NO RENDER

import os
from pathlib import Path
from decouple import config  # Importar 'config' do decouple
import dj_database_url  # Importar 'dj_database_url'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Esta linha está CORRETA para sua estrutura (projetorestaurante/restaurante/settings.py)
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# Lendo SECRET_KEY e DEBUG do arquivo .env ou das variáveis de ambiente do Render
SECRET_KEY = config('SECRET_KEY')
DEBUG = True


# Ajustado para ler do .env ou do Render
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fila',
    'cardapio',
    'controle',
    'clientes',
    'reservas',
    'comandas',
    'usuarios',
    'estoque',
    'whitenoise.runserver_nostatic', # Adiciona whitenoise para servir estáticos (mesmo com DEBUG=True local, se necessário)
    'anymail',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- 1. CORREÇÃO DO CSS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'restaurante.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Corretamente aponta para 'projetorestaurante/templates'
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'fila.context_processors.informacoes_fila',
                'fila.context_processors.staff_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'restaurante.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# --- 2. CORREÇÃO DO SUPERUSER (Banco de Dados) ---
# Lê a variável DATABASE_URL do Render (ou do .env local)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}



# Password validation
# (Seu código original estava bom)
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Configuração de arquivos de Mídia (uploads dos usuários)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_ROOT = BASE_DIR.parent / 'staticfiles_coletados'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# --- 1. CORREÇÃO DO CSS (Armazenamento Whitenoise) ---
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'




# Outras Configurações
RESTAURANTE_CAPACIDADE_POR_HORARIO = 50
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'perfil'
LOGOUT_REDIRECT_URL = 'inicio'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- 3. CORREÇÃO DO E-MAIL (Resend via Anymail) ---
if not DEBUG: # PRODUÇÃO (Render)
    INSTALLED_APPS += ['anymail']  # Garante que o anymail está ativo em produção
    
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
    ANYMAIL = {
        "RESEND_API_KEY": os.environ.get('RESEND_API_KEY'),
    }
    # O e-mail de envio da Resend (inicialmente use o onboarding)
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', "onboarding@resend.dev")
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
else: # LOCAL
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'Chama do Cerrado <nao-responda@chamadocerrado.com.br>'