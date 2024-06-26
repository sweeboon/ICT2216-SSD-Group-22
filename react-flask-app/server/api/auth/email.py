from flask import render_template, current_app
from flask_mailman import EmailMessage

def send_email(subject, recipient, template, **kwargs):
    msg = EmailMessage(
        subject=subject,
        from_email=current_app.config['MAIL_DEFAULT_SENDER'],
        to=[recipient],
    )
    msg.body = render_template(f'{template}.txt', **kwargs)
    msg.html = render_template(f'{template}.html', **kwargs)
    msg.send()
