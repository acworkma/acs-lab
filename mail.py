from azure.communication.email import EmailClient
from dotenv import load_dotenv
import os

def main():
    try:
        load_dotenv()

        connection_string_email = os.getenv("CONNECTION_STRING_EMAIL")
        if not connection_string_email:
            raise ValueError("CONNECTION_STRING_EMAIL not found in environment variables.")
        sender_address = os.getenv("SENDER_ADDRESS")
        if not sender_address:
            raise ValueError("SENDER_ADDRESS not found in environment variables.")
        recipient_address = os.getenv("RECIPIENT_ADDRESS")
        if not recipient_address:
            raise ValueError("RECIPIENT_ADDRESS not found in environment variables.")
        client = EmailClient.from_connection_string(connection_string_email)

        message = {
            "senderAddress": sender_address,
            "recipients": {
                "to": [{"address": recipient_address}]
            },
            "content": {
                "subject": "Test Email",
                "plainText": """Hello world via email.""",
                "html": """
                <html>
                    <body>
                        <h1>
                            Hello world via email.
                        </h1>
                    </body>
                </html>"""
            },
        }

        poller = client.begin_send(message)
        result = poller.result()
        print("Message sent: ", result["messageId"])

    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()
