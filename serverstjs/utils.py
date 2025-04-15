# utils.py
import random
from django.core.mail import send_mail

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):
    subject = 'Código de verificación'
    message = f'Tu código de verificación es: {code}'
    send_mail(subject, message, 'holamellamodaniel1998@gmail.com', [email])
