import os

from dotenv import load_dotenv
import mindsdb_sdk
from mindsdb_sdk.server import Server

from grepmail.mindsdb.handlers.common import create_and_get_project
from grepmail.mindsdb.handlers.email import create_and_get_email_db, query_email_db, create_and_get_email_kb
    
load_dotenv()

EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PWD = os.getenv('EMAIL_PWD')


if __name__ == '__main__':
    server = mindsdb_sdk.connect('http://127.0.0.1:47334')
    project = create_and_get_project(server, "grepmail")
    email_db = create_and_get_email_db(server, EMAIL_ID, EMAIL_PWD)

    # Perform operations with the email database
    if email_db:
        print(f"Connected to email database: {email_db.name}")

        # Example query
        # query = f"SELECT * FROM {email_db.name}.emails LIMIT 5"
        # results = query_email_db(server, EMAIL_ID, query)

        # if not results.empty:
        #     print("Query results:")
        #     with open('query_results.txt', 'w') as f:
        #         f.write(results.to_string())
        #     print(results)
        # else:
        #     print("No results found.")

    email_kb = create_and_get_email_kb(project, EMAIL_ID)
    project.knowledge_bases.list()
