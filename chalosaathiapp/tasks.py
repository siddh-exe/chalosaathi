# chalosaathiapp/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Booking, Ride
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_booking_status_notificatio_email(booking_id, status):
    try:
        booking = Booking.objects.get(id=booking_id)
        ride = booking.ride
        passenger = booking.passenger
        subject = f'Booking {status.title()} - {ride.pickup} to {ride.destination}'
        html_message = render_to_string('emails/booking_status_notification.html', {
            'booking': booking, 'ride': ride, 'passenger': passenger,
            'passenger_name': f'{passenger.first_name} {passenger.last_name}'.strip() or passenger.username,
            'status': status.title(),
        })
        plain_message = strip_tags(html_message)
        send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [passenger.email],
                  html_message=html_message, fail_silently=False)
        logger.info(f'Booking {status} email sent for booking {booking_id} to {passenger.email}')
    except Exception as e:
        logger.error(f'Failed to send {status} email for booking {booking_id}: {str(e)}')

@shared_task
def send_booking_status_notification_email(booking_id, status):
    try:
        booking = Booking.objects.get(id=booking_id)
        ride = booking.ride
        passenger = booking.passenger
        passenger_name = f'{passenger.first_name} {passenger.last_name}'.strip() or passenger.username
        subject = f'Booking {status.title()} - {ride.pickup} to {ride.destination}'
        message = render_to_string('emails/booking_status_notification.txt', {
            'booking': booking,
            'ride': ride,
            'passenger': passenger,
            'passenger_name': passenger_name,
            'status': status.title(),
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [passenger.email],
            fail_silently=False,
        )
        logger.info(f'Booking {status} email sent for booking {booking_id} to {passenger.email}')
    except Booking.DoesNotExist:
        logger.error(f'Booking {booking_id} not found for status {status} email')
    except Exception as e:
        logger.error(f'Failed to send {status} email for booking {booking_id}: {str(e)}')

@shared_task
def send_booking_notification_email(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        ride = booking.ride
        passenger = booking.passenger
        subject = f'New Booking Request - {ride.pickup} to {ride.destination}'
        html_message = render_to_string('emails/booking_notification.html', {
            'booking': booking, 'ride': ride, 'passenger': passenger,
            'passenger_name': f'{passenger.first_name} {passenger.last_name}'.strip() or passenger.username,
            'passenger_email': passenger.email, 'passenger_phone': booking.contact_number or 'Not provided',
        })
        plain_message = strip_tags(html_message)
        send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [ride.user.email],
                  html_message=html_message, fail_silently=False)
        logger.info(f'Booking email sent for booking {booking_id} to {ride.user.email}')
    except Exception as e:
        logger.error(f'Failed to send booking email for booking {booking_id}: {str(e)}')