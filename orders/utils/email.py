import threading
import requests
from django.conf import settings
from django.template.loader import render_to_string

def send_order_confirmation_via_mailgun(email, order_data):
    subject = "Payment Confirmation - Your Subscription is Paid"

    # Render templates
    text_message = render_to_string("emails/order_confirmation.txt", {
        "email": email,
        "order": order_data
    })

    html_message = render_to_string("emails/order_confirmation.html", {
        "email": email,
        "order": order_data
    })

    # Send via Mailgun API
    requests.post(
        f"{settings.ANYMAIL['MAILGUN_API_URL']}/{settings.ANYMAIL['MAILGUN_SENDER_DOMAIN']}/messages",
        auth=("api", settings.ANYMAIL["MAILGUN_API_KEY"]),
        data={
            "from": f"FinMark by Imperionite <{settings.DEFAULT_FROM_EMAIL}>",
            "to": [email],
            "subject": subject,
            "text": text_message,
            "html": html_message,
        },
        timeout=10
    )

def trigger_order_confirmation_email(email, order_data):
    thread = threading.Thread(target=send_order_confirmation_via_mailgun, args=(email, order_data))
    thread.start()
