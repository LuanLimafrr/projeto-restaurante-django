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
        sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)
        
        # Estas linhas serão impressas nos logs do Render
        print(f"DEBUG: E-mail para {to_email} enviado com Status: {response.status_code}")
        print(f"DEBUG: Headers: {response.headers}")
        print(f"DEBUG: Body: {response.body}")
        
        if response.status_code >= 200 and response.status_code < 300:
            return True
        else:
            print(f"Erro ao enviar email via SendGrid API. Status: {response.status_code}, Body: {response.body}")
            return False
    except Exception as e:
        print(f"Exceção ao enviar email via SendGrid API: {e}")
        return False