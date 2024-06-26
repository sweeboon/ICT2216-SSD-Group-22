from flask import render_template
from flask_mailman import EmailMessage
from api import mail

def send_email(subject, recipient, template, **kwargs):
    msg = EmailMessage(
        subject=subject,
        from_email='noreply@yourdomain.com',
        to=[recipient],
    )
    msg.body = render_template(f'{template}.txt', **kwargs)
    msg.html = render_template(f'{template}.html', **kwargs)
    mail.send(msg)