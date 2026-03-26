import logging
from decimal import Decimal
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Alert, Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)

def _fire_alert(alert, current_value, label):
    now = timezone.now()
    alert.is_active = False
    alert.triggered_at = now
    alert.save(update_fields=['is_active', 'triggered_at'])

    title = f"Alert: {alert.symbol} - {alert.get_alert_type_display()}"
    body = (
        f'{alert.symbol}: {label}. '
        f'Current value: {current_value}. '
        f'Triggered at {now.strftime("%Y-%m-%d %H:%M UTC")}.'
    )
    notif = Notification.objects.create(
        user = alert.user,
        alert = alert,
        title = title,
        body = body,
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{alert.user.id}',
        {
            'type': 'send_notification',
            'id':notif.id,
            'title':notif.title,
            'body':notif.body,

        }
    )
    send_alert_email.delay(notif.id)
    logger.info('Alert fired and pushed %s', title)

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def evaluate_alerts(self, symbol, current_price, rsi=None, macd_signal=None, detected_patterns=None):
    try:
        price = Decimal(str(current_price))
        alerts = Alert.objects.filter(
            symbol__iexact=symbol,
            is_active = True
            ).select_related('user')
        
        for alert in alerts:
            t = alert.alert_type

            if t == 'price_above' and alert.threshold is not None:
                if price >= alert.threshold:
                    _fire_alert(alert, price,
                                f'price crossed above {alert.threshold}')

            elif t == 'price_below' and alert.threshold is not None:
                if price <= alert.threshold:
                    _fire_alert(alert, price,
                                f'price dropped below {alert.threshold}')

            elif t == 'rsi_above' and rsi is not None and alert.threshold is not None:
                if Decimal(str(rsi)) >= alert.threshold:
                    _fire_alert(alert, f'RSI {rsi:.1f}',
                                f'RSI rose above {alert.threshold}')

            elif t == 'rsi_below' and rsi is not None and alert.threshold is not None:
                if Decimal(str(rsi)) <= alert.threshold:
                    _fire_alert(alert, f'RSI {rsi:.1f}',
                                f'RSI fell below {alert.threshold}')

            elif t == 'macd_cross_up' and macd_signal == 'bullish':
                _fire_alert(alert, 'MACD bullish crossover',
                            'MACD crossed above signal line')

            elif t == 'macd_cross_dn' and macd_signal == 'bearish':
                _fire_alert(alert, 'MACD bearish crossover',
                            'MACD crossed below signal line')

            elif t == 'pattern' and detected_patterns:
                for p in detected_patterns:
                    if p.lower() == alert.pattern_name.lower():
                        _fire_alert(alert, f'pattern "{alert.pattern_name}" detected',
                                    f'{alert.pattern_name} found on {symbol}')
                        break  # don't double-fire the same alert

    except Exception as exc:
        logger.exception('evaluate_alerts failed for %s', symbol)
        raise self.retry(exc=exc)
    

@shared_task(bind=True, max_retires=3, default_retry_delay=30)
def send_alert_email(self, notification_id):
    try:
        notif = Notification.objects.select_related('user', 'alert').get(pk=notification_id)
        user = notif.user

        if not user.email:
            logger.info(f"No email for user {user.username} ")
            return
        
        html_body = render_to_string('alerts/email/alert_triggered.html',{
            'user':user,
            'notification':notif,
        })

        send_mail(
            subject=notif.title,
            message=notif.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_body,
            fail_silently=False,
        )
        logger.info(f'Alert email sent to {user.email}')
    
    except Notification.DoesNotExist:
        logger.error('send_alert_email: Notification %s not found', notification_id)
    except Exception as exc:
        logger.exception('send_alert_email failed for notification %s', notification_id)
        raise self.retry(exc=exc)