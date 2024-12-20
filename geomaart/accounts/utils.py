import random
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os


def send_otp(phone_number):
    try :
       client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
       verify = client.verify.services(os.environ['TWILIO_VERIFY_SERVICE_SID'])
       verify.verifications.create(
           to=phone_number,  
           channel='sms' ,
       )
       return {'status':True,'message':"we have send a otp to you number"}
    except TwilioRestException as e:
       return {'status':False,'message':f"Twilio error occurred {e}"}
    except ConnectionError as e:
       return {'status':False,'message':f"Network error occurred. {e}"}
    except TimeoutError as e:
       return {'status':False,'message':f"The request timed out. {e}"}
    except Exception as e:
       return {'status':False,'message':f"An unexpected error occurred: {e}"}
def validate_otp(phone_number, otp_code):
    try :
       client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
       verify = client.verify.services(os.environ['TWILIO_VERIFY_SERVICE_SID'])
    
       verification_check = verify.verification_checks.create(
           to=phone_number,
           code=otp_code
       )
       if verification_check.status == "approved" :
           return True
       else :
           print(verification_check.status)
           return "OTP verification failed Please try again"
    except TwilioRestException  as e :
        if e.status == 404:
            return "something went wrong please try again"
        elif e.status == 400:
            return "Invalid OTP or request format."
        elif e.status == 429:
            return "Too many attempts. Please wait and try again later."
        else:
            return f"An unexpected error occurred: {e.msg}"

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
