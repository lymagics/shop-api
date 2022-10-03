from threading import Thread

from flask import current_app, render_template, Flask
from flask_mail import Message

from . import mail 


def send_async_email(msg: Message, app: Flask):
    """Send mail asynchronously.
    
    :param msg: message to send.
    :param app: flask application object.
    """
    with app.app_context():
        mail.send(msg)


def send_mail(subject: str, to: str, template: str, **kwargs):
    """Send mail to user.
    
    :param subject: message subject.
    :param to: message recipient.
    :param template: name of template to render.
    """
    app = current_app._get_current_object()
    msg = Message(subject)

    msg.sender = current_app.config["MAIL_USERNAME"]
    msg.recipients = [to]
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)

    thr = Thread(target=send_async_email, args=[msg, app])
    thr.start()
    return thr 
