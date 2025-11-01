# projetorestaurante/restaurante/utils/emails.py

import os
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_with_sendgrid_api(to_email, subject, html_content, from_email=None):
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
   # ATENÇÃO: ALTERAÇÃO TEMPORÁRIA APENAS PARA TESTE
        # sendgrid_client = SendGridAPIClient(sendgrid_api_key) # LINHA ORIGINAL
        sendgrid_client = SendGridAPIClient("SG.FAKE_API_KEY_FOR_TESTING_ONLY") # <--- USE UMA CHAVE FALSA AQUI TEMPORARIAMENTE
        # FIM DA ALTERAÇÃO TEMPORÁRIA

        response = sendgrid_client.send(message)
    except Exception as e:
        print(f"Exceção ao enviar email via SendGrid API: {e}")
        return False