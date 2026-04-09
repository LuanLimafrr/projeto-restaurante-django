# /projetorestaurante/restaurante/settings.py
# VERSÃO FINAL CORRIGIDA PARA APRESENTAÇÃO - RENDER

import os
from pathlib import Path
from decouple import config
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURAÇÕES BÁSICAS ---
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)

# Ajustado para ler do .env ou do Render
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

# --- APPLICATION DEFINITION ---
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
    'whitenoise.runserver_nostatic',
    # 'anymail' removido daqui para evitar duplicidade com o bloco 'if not DEBUG'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        'DIRS': [
            # Estratégia multi-caminho para não falhar no Render
            os.path.join(BASE_DIR, 'templates'),
            BASE_DIR / 'templates',
            '/opt/render/project/src/projetorestaurante/projetorestaurante/templates',
        ],
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

# --- BANCO DE DADOS ---
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}

# --- VALIDAÇÃO DE SENHA ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# --- ARQUIVOS ESTÁTICOS E MÍDIA ---
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR.parent / 'staticfiles_coletados'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- OUTRAS CONFIGURAÇÕES ---
RESTAURANTE_CAPACIDADE_POR_HORARIO = 50
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'perfil'
LOGOUT_REDIRECT_URL = 'inicio'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURAÇÃO DE E-MAIL (PRODUÇÃO VS LOCAL) ---
if not DEBUG:
    # Em produção no Render
    if 'anymail' not in INSTALLED_APPS:
        INSTALLED_APPS += ['anymail']
    
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
    ANYMAIL = {
        "RESEND_API_KEY": os.environ.get('RESEND_API_KEY'),
    }
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', "onboarding@resend.dev")
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
else:
    # Localmente (DEBUG=True)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'Chama do Cerrado <nao-responda@chamadocerrado.com.br>'