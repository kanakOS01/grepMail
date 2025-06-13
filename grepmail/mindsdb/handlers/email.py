import os

from dotenv import load_dotenv

from grepmail.logger import logger
from grepmail.mindsdb.handlers.base import Base

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
        self._create_email_db(EMAIL_ID, EMAIL_PWD)


    def _create_email_db(self, email: str, password: str) -> None:
        """
        Create an email database in MindsDB with the given email and password if it doesn't already exist.

        Args:
            email (str): The email address.
            password (str): The password for the email account.    
        """
        db_name_list = [db.name for db in self.server.list_databases()]
        if 'email_db' not in db_name_list:
            logger.info("Creating email database...")
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
                logger.info(f"Email database '{email_db.name}' created successfully.")
            else:
                logger.error("Failed to create email database.")
        else:
            logger.info("Email database already exists. Skipping creation.")
