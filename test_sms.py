# test_sms.py
import os
from twilio.rest import Client

def send_test():
    try:
        sid = os.environ.get("TWILIO_ACCOUNT_SID")
        token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_num = os.environ.get("TWILIO_PHONE")
        to_num = os.environ.get("MY_PHONE")

        if not all([sid, token, from_num, to_num]):
            raise SystemExit("Missing one of the required env vars: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE, MY_PHONE")

        client = Client(sid, token)
        msg = client.messages.create(
            body="Test SMS from Tamil Nadu Stock Advisor — If you receive this, Twilio works!",
            from_=from_num,
            to=to_num
        )
        print("Message SID:", msg.sid, "Status:", msg.status)
    except Exception as e:
        print("ERROR while sending SMS:", repr(e))

if __name__ == "__main__":
    send_test()
