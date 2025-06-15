import os

from dotenv import load_dotenv
import mindsdb_sdk

from grepmail.mindsdb.handlers.common import create_and_get_project
from grepmail.mindsdb.handlers.email import create_and_get_email_db, query_email_db, create_and_get_email_kb, create_and_get_storage, bulk_insert_email_kb
    
load_dotenv()

EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PWD = os.getenv('EMAIL_PWD')


if __name__ == '__main__':
    server = mindsdb_sdk.connect('http://127.0.0.1:47334')
    project = create_and_get_project(server, "grepmail")
    email_db = create_and_get_email_db(server, EMAIL_ID, EMAIL_PWD)
    email_vs = create_and_get_storage(server, EMAIL_ID)
    email_kb = create_and_get_email_kb(project, EMAIL_ID)

    bulk_insert_email_kb(project, email_kb, email_db)

    print("------------------------------------")
    print(server.databases.list())
    print(project.knowledge_bases.list())
    print("------------------------------------")


    # project.knowledge_bases.drop('email_kb_tanwarkanak2')
    # server.databases.drop('email_db_tanwarkanak2')
    # server.databases.drop('pg_vs_tanwarkanak2')
    # server.databases.drop('email_db_tanwarkanak2_chromadb')


    # Perform operations with the email database
    # if email_db:
    #     print(f"Connected to email database: {email_db.name}")

    #     # Example query
    #     # query = f"SELECT * FROM {email_db.name}.emails LIMIT 5"
    #     # results = query_email_db(server, EMAIL_ID, query)

    #     # if not results.empty:
    #     #     print("Query results:")
    #     #     with open('query_results.txt', 'w') as f:
    #     #         f.write(results.to_string())
    #     #     print(results)
    #     # else:
    #     #     print("No results found.")

    # create_and_get_storage(server, EMAIL_ID)
    # # email_kb = create_and_get_email_kb(project, EMAIL_ID)
    # server.databases.list()
    # project.knowledge_bases.list()
