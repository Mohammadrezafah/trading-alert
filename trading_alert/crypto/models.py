from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.urls import reverse
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from model_utils import Choices
from model_utils.models import TimeStampedModel

User = get_user_model()

class CriptoAlert(TimeStampedModel):
    OPERATOR = Choices(">=", "<=")
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    operator = models.CharField(choices=OPERATOR, max_length=255)
    price = models.FloatField()
    notif_to = models.ManyToManyField(User)
    limit_notif = models.IntegerField(default=5)
    success_notif = models.IntegerField(default=0)
    interval_check = models.IntegerField(default=1) # in minute
    task = models.ForeignKey(
        PeriodicTask, on_delete=models.SET_NULL, blank=True, null=True
    )
    current_price = models.FloatField(default=0)
    currency = models.CharField(max_length=255, default="IDR")

    def __str__(self):
        return f"{self.code} - {self.title}"

    class Meta:
        ordering = ["id"]

def create_periodic_task(sender, instance, created, **kwargs):
    from trading_alert.crypto.tasks import get_current_price
    interval, created = IntervalSchedule.objects.update_or_create(
        every=instance.interval_check, period="minutes"
    )
    if not instance.task:
        task = PeriodicTask.objects.update_or_create(
            name=f"notification-crypto-{instance.id}",
            defaults={
                "interval": interval,
                "task": "trading_alert.crypto.tasks.send_alert_crypto",
                "kwargs": '{"crpyto_id":%s}' % (instance.id),
                # "one_off": True,
                "enabled": True
            },
        )
        instance.task = task

        # instance.currency_price = get_current_price(instance)
        instance.save()
    elif instance.task.interval != interval:
        instance.task.interval = interval        

def delete_periodic_task(sender, instance, **kwargs):
    instance.task.delete()
    
post_save.connect(create_periodic_task, sender=CriptoAlert)
post_delete.connect(delete_periodic_task, sender=CriptoAlert)
