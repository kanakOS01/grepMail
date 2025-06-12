import os
from smtplib import SMTP
from venv import create

import mindsdb_sdk
from dotenv import load_dotenv
import mindsdb_sdk.databases

from grepmail.mindsdb.integrations.base import Base

# Load environment variables
load_dotenv()

EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PWD = os.getenv('EMAIL_PWD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = os.getenv('SMTP_PORT', 587)
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')


class EmailHandler(Base):
    def __init__(
        self,
        mindsdb_server_url: str = "http://127.0.0.1:47334",
        project_name: str = "grepmail"
    ):
        super().__init__(mindsdb_server_url, project_name)
        self._create_email_database(EMAIL_ID, EMAIL_PWD)


    def _create_email_database(self, email: str, password: str):
        """
        Create an email database in MindsDB with the given email and password.
        """
        db_name_list = [db.name for db in self.server.list_databases()]
        if 'email_db' not in db_name_list:
            print("Creating email database...")
            email_db = self.server.create_database(
                name='email_db',
                engine='email',
                connection_args={
                    "email": email,
                    "password": password,
                    "smtp_server": SMTP_SERVER,
                    "smtp_port": SMTP_PORT,
                    "imap_server": IMAP_SERVER
                }
            )

            if email_db:
                print(f"Email database '{email_db.name}' created successfully.")
            else:
                print("Failed to create email database.")
        else:
            print("Email database already exists. Skipping creation.")
