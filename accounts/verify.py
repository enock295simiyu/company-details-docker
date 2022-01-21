from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from company_details.settings import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, TWILIO_VERIFY_SERVICE_SID

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
verify = client.verify.services(TWILIO_VERIFY_SERVICE_SID)


def send_code(phone):
    verify.verifications.create(to=phone, channel='sms')


def check_code(phone, code):
    try:
        result = verify.verification_checks.create(to=phone, code=code)
    except TwilioRestException:
        print('no')
        return False
    return result.status == 'approved'
