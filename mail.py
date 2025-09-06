from azure.communication.email import EmailClient
from dotenv import load_dotenv
import os

def main():
    try:
        load_dotenv()
        connection_string_email = os.getenv("CONNECTION_STRING_EMAIL")
        if not connection_string_email:
            raise ValueError("CONNECTION_STRING_EMAIL not found in environment variables.")
        client = EmailClient.from_connection_string(connection_string_email)

        message = {
            "senderAddress": "DoNotReply@e1267993-ef04-4b33-99d6-046370f5db15.azurecomm.net",
            "recipients": {
                "to": [{"address": "admin@MngEnvMCAP818246.onmicrosoft.com"}]
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
