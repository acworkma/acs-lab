import os
from azure.communication.sms import SmsClient
from dotenv import load_dotenv

try:
    load_dotenv()
    connection_string_sms = os.getenv("CONNECTION_STRING_SMS")
    if not connection_string_sms:
        raise ValueError("CONNECTION_STRING_SMS not found in environment variables.")
    sms_from = os.getenv("SMS_FROM")
    if not sms_from:
        raise ValueError("SMS_FROM not found in environment variables.")
    sms_to = os.getenv("SMS_TO")
    if not sms_to:
        raise ValueError("SMS_TO not found in environment variables.")

    sms_client = SmsClient.from_connection_string(connection_string_sms)

    sms_responses = sms_client.send(
        from_=sms_from,
        to=sms_to,
        message='''Hello World 👋🏻 via SMS'''
    )
except Exception as ex:
    print(ex)
