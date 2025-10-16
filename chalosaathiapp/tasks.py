# chalosaathiapp/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Booking, Ride
import logging
from django.core.mail import EmailMultiAlternatives
logger = logging.getLogger(__name__)

@shared_task
def send_booking_status_notificatio_email(booking_id, status):
    try:
        booking = Booking.objects.get(id=booking_id)
        ride = booking.ride
        passenger = booking.passenger
        driver = ride.user  # The one who created the ride

        # Base cost and subscription details
        base_cost = ride.cost
        subscription_type = booking.subscription_type

        if subscription_type == 'weekly':
            total_cost = base_cost * 1.5
            plan_name = 'Weekly Plan (7 Rides)'
        elif subscription_type == 'monthly':
            total_cost = base_cost * 5
            plan_name = 'Monthly Plan (30 Rides)'
        elif subscription_type == 'quarterly':
            total_cost = base_cost * 14
            plan_name = 'Quarterly Plan (90 Rides)'
        else:
            total_cost = base_cost
            plan_name = 'One-Time Ride'

        subject = f'Booking {status.title()} - {ride.pickup} to {ride.destination}'
        html_message = render_to_string('emails/booking_status_notification.html', {
            'booking': booking,
            'ride': ride,
            'passenger_name': getattr(passenger, 'full_name', None) or passenger.email,
            'driver_name': getattr(driver, 'full_name', None) or driver.email,
            'status': status.title(),
            'plan_name': plan_name,
            'total_cost': total_cost,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [passenger.email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f'Booking {status} email sent for booking {booking_id} to {passenger.email}')

    except Exception as e:
        logger.error(f'Failed to send {status} email for booking {booking_id}: {str(e)}')

@shared_task
def send_booking_status_notification_email(booking_id, status):
    try:
        booking = Booking.objects.get(id=booking_id)
        ride = booking.ride
        passenger = booking.passenger
        driver = ride.user  # The one who created the ride

        # Base cost and subscription details
        base_cost = ride.cost
        subscription_type = booking.subscription_type

        if subscription_type == 'weekly':
            total_cost = base_cost * 1.5
            plan_name = 'Weekly Plan (7 Rides)'
        elif subscription_type == 'monthly':
            total_cost = base_cost * 5
            plan_name = 'Monthly Plan (30 Rides)'
        elif subscription_type == 'quarterly':
            total_cost = base_cost * 14
            plan_name = 'Quarterly Plan (90 Rides)'
        else:
            total_cost = base_cost
            plan_name = 'One-Time Ride'

        subject = f'Booking {status.title()} - {ride.pickup} to {ride.destination}'
        html_message = render_to_string('emails/booking_status_notification.html', {
            'booking': booking,
            'ride': ride,
            'passenger_name': getattr(passenger, 'full_name', None) or passenger.email,
            'driver_name': getattr(driver, 'full_name', None) or driver.email,
            'status': status.title(),
            'plan_name': plan_name,
            'total_cost': total_cost,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [passenger.email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f'Booking {status} email sent for booking {booking_id} to {passenger.email}')

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
            'passenger_name': f'{passenger.full_name}'.strip() or passenger.username,
            'passenger_email': passenger.email, 'passenger_phone': booking.contact_number or 'Not provided',
        })
        plain_message = strip_tags(html_message)
        send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [ride.user.email],
                  html_message=html_message, fail_silently=False)
        logger.info(f'Booking email sent for booking {booking_id} to {ride.user.email}')
    except Exception as e:
        logger.error(f'Failed to send booking email for booking {booking_id}: {str(e)}')

@shared_task
def send_booking_email(driver_email, driver_name, passenger_name, ride_info, subscription_type, total_cost):
    """
    Sends an HTML email to the driver notifying about the subscription booking.
    """
    subject = 'New Booking Confirmation - Subscription Selected'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [driver_email]

    html_content = render_to_string('booking_email.html', {
        'driver_name': driver_name,
        'passenger_name': passenger_name,
        'ride': ride_info,
        'subscription_type': subscription_type.title(),
        'total_cost': round(total_cost, 2),
    })

    try:
        msg = EmailMultiAlternatives(subject, '', from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return f"Email sent to {driver_email}"
    except Exception as e:
        return f"Failed to send email to {driver_email}: {str(e)}"