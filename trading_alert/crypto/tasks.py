import logging

import cryptocompare
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage

from config import celery_app
from trading_alert.crypto.models import CriptoAlert

User = get_user_model()
# Get an instance of a logger
logger = logging.getLogger(__name__)

def send_email_crypto(cripto_alert):
    subject = f"Segera check {cripto_alert.code}"
    body = f"{cripto_alert.code} sudah mencapai target {cripto_alert.operator} {cripto_alert.price}"

    email = EmailMessage(
        subject, body, settings.DEFAULT_FROM_EMAIL, [user.email for user in cripto_alert.notif_to.all()], [],
    )
    email.send()

def get_current_price(cripto_alert):
    price = 0
    try:
        price = float(
            cryptocompare.get_price(
                cripto_alert.code, 
                currency=cripto_alert.currency
            )[cripto_alert.code][cripto_alert.currency])
    except Exception as e:
        logger.error(str(e))
    logger.info(f"Price is   : {price}")
    return price
@celery_app.task()
def send_alert_crypto(crpyto_id):
    cripto_alert = CriptoAlert.objects.filter(pk=crpyto_id).first()
    if not cripto_alert:
        logger.error("CriptoAlert objects not found")
        return "CriptoAlert objects not found"
    if cripto_alert.limit_notif >= cripto_alert.success_notif:
        cripto_alert.currency_price = get_current_price(cripto_alert)
        is_email = False
        if cripto_alert.currency_price != 0 and eval(
                f"{cripto_alert.currency_price} {cripto_alert.operator} {cripto_alert.price}"
            ):
            send_email_crypto(cripto_alert)
            cripto_alert.success_notif =  cripto_alert.success_notif  + 1
        cripto_alert.save()
    return True
