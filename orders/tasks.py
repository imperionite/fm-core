from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(name="orders.send_order_confirmation_email")
def send_order_confirmation_email(email, order_data):
    subject = "Payment Confirmation - Your Subscription is Paid"
    message = (
        f"Hi {email},\n\n"
        "Here's a summary of your order:\n\n"
    )
    
    for item in order_data['items']:
        message += f"- {item['name']} (x{item['quantity']}): ₱{item['price']}\n"

    message += (
        f"\nTotal: ₱{order_data['total']}\n\n"
        "We’re processing your subscription and will notify you once it is available.\n\n"
        "Thank you!\n\n"
        "— The FinMark by Imperionite Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
