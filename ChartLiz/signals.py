# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Transaction

@receiver(post_save, sender=User)
def create_transaction_for_user(sender, instance, created, **kwargs):
    if created:
        Transaction.objects.create(user=instance)
