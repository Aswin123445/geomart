import re
import random
import os
from django.core.mail import send_mail
from datetime import datetime
def format_phone_number(phone_number):
    phone_number = re.sub(r'[^0-9+]', '', phone_number)
    if not phone_number.startswith('+91'):
        # If not, add '+91' at the start
        phone_number = '+91' + phone_number.lstrip('0')  # Remove any leading zeroes if present
    if len(phone_number) == 13 and re.match(r'^\+91\d{10}$', phone_number):
        return phone_number
    else:
        raise ValueError("Invalid phone number format. Must be a 10-digit number starting with +91.")
    
def send_otp_email(user_email):
    otp= random.randint(100000,999999)
    subject = 'Geomart gmail verification otp'
    message = f'Dear custom verifiy your email address with user the otp number {otp} and explore geomaart'
    send_mail(subject=subject,message=message,from_email=os.environ.get('GMAIL_ID'),recipient_list=[user_email])
    return otp

def converter(date):
    date_object = datetime.strptime(date, "%m/%d/%Y")
    formatted_date = date_object.strftime("%Y-%m-%d")
    return formatted_date