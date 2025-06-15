import os

from dotenv import load_dotenv
from httpx import get
from mindsdb_sdk.server import Server
from mindsdb_sdk.databases import Database
from mindsdb_sdk.projects import Project
from mindsdb_sdk.knowledge_bases import KnowledgeBase
from pandas import DataFrame

from grepmail.logger import logger

# Load environment variables
load_dotenv()

EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PWD = os.getenv('EMAIL_PWD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PG_VECTOR_HOST = os.getenv('PG_VECTOR_HOST')
PG_VECTOR_PORT = int(os.getenv('PG_VECTOR_PORT'))
PG_VECTOR_USER = os.getenv('PG_VECTOR_USER')
PG_VECTOR_PASSWORD = os.getenv('PG_VECTOR_PASSWORD')
PG_VECTOR_DB = os.getenv('PG_VECTOR_DB')


def get_email_db_name(email: str) -> str:
    """
    Generate a database name based on the email address.
    """
    return f'email_db_{email.split("@")[0]}'


def create_and_get_email_db(server: Server, email: str, password: str) -> Database | None:
    """
    Create an email database in MindsDB if it doesn't exist.

    Args:
        server (Server): The MindsDB server instance.
        email (str): The email address to create the database for.
        password (str): The password for the email account.
    """
    db_name = get_email_db_name(email)
    db_names = [db.name for db in server.list_databases()]

    if db_name not in db_names:
        logger.info(f"Creating email database '{db_name}'...")
        email_db = server.create_database(
            name=db_name,
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
            return email_db
        
        logger.error("Failed to create email database.")
        return None
    
    else:
        logger.info(f"Email database '{db_name}' already exists. Skipping creation.")

    return server.get_database(db_name)


def delete_email_db(server: Server, email: str) -> None:
    """
    Delete the email database if it exists.

    Args:
        server (Server): The MindsDB server instance.
        email (str): The email address associated with the database to delete.
    """
    db_name = get_email_db_name(email)
    db_names = [db.name for db in server.list_databases()]

    if db_name in db_names:
        logger.info(f"Deleting email database '{db_name}'...")
        server.drop_database(db_name)
        logger.info("Email database deleted successfully.")
    else:
        logger.info("Email database does not exist. Skipping deletion.")


def query_email_db(server: Server, email: str, query: str) -> DataFrame | None:
    """
    Query the email database.

    Args:
        server (Server): The MindsDB server instance.
        email (str): The email address associated with the database.
        query (str): The SQL query to execute on the email database.
    """
    db_name = get_email_db_name(email)
    email_db = server.get_database(db_name)

    if email_db:
        return email_db.query(query).fetch()
    else:
        logger.error(f"Email database '{db_name}' not found.")
        return None


def get_storage_name(email: str) -> str:
    """
    Generate a storage name for the PostgreSQL vector storage.
    """
    return f'pg_vs_{email.split("@")[0]}'


def create_and_get_storage(server: Server, email: str) -> Database | None:
    """
    Create a PostgreSQL vector storage in MindsDB.

    Args:
        server (Server): The MindsDB server instance.
        email (str): The email address to create the storage for.
    """
    vs_name = get_storage_name(email)
    db_names = [db.name for db in server.list_databases()]
    if vs_name not in db_names:
        logger.info(f"Creating storage '{vs_name}'...")
        # pg_vs = server.create_database(
        #     engine='postgres',
        #     name=vs_name,
        #     connection_args={
        #         "host": PG_VECTOR_HOST,
        #         "port": PG_VECTOR_PORT,
        #         "database": PG_VECTOR_DB,
        #         "user": PG_VECTOR_USER,
        #         "password": PG_VECTOR_PASSWORD,
        #         "distance": "cosine",
        #     }
        # )

        create_query = f"""CREATE DATABASE {vs_name}
WITH ENGINE = 'pgvector',
PARAMETERS = {{
    "host":  "{PG_VECTOR_HOST}",
    "port": {PG_VECTOR_PORT},
    "database": "{PG_VECTOR_DB}",
    "user": "{PG_VECTOR_USER}",
    "password": "{PG_VECTOR_PASSWORD}",
    "distance": "cosine"
}};
"""

        # if pg_vs:
        #     logger.info(f"Storage '{pg_vs.name}' created successfully.")
        #     return pg_vs
        
        # logger.error("Failed to create storage.")
        # return None
    
        server.query(create_query).fetch()
        try:
            pg_vs = server.databases.get(vs_name)
            logger.info(f"Storage '{pg_vs.name}' created successfully.")
            return pg_vs
        except Exception as e:
            logger.error("Failed to create storage.")
            return None

    else:
        logger.info(f"Storage '{vs_name}' already exists. Skipping creation.")

    return server.get_database(vs_name)


def get_email_kb_name(email: str) -> str:
    """
    Generate a knowledge base name based on the email address.
    """
    return f'email_kb_{email.split("@")[0]}'


def create_and_get_email_kb(project: Project, email: str) -> KnowledgeBase | None:
    """
    Create an email knowledge base in MindsDB.

    Args:
        project (Project): The MindsDB project instance.
        email (str): The email address to create the knowledge base for.
    """
    kb_name = get_email_kb_name(email)
    vs_name = get_storage_name(email)
    kb_names = [kb.name for kb in project.knowledge_bases.list()]

    if kb_name not in kb_names:
        logger.info(f"Creating email knowledge base '{kb_name}'...")
        create_query = f"""CREATE KNOWLEDGE_BASE {kb_name}
USING
    embedding_model = {{
        "provider": "ollama",
        "model_name": "nomic-embed-text",
        "base_url": "http://localhost:11434"
    }},
    reranking_model = {{
        "provider": "gemini",
        "model_name": "gemini-2.0-flash",
        "api_key": "{GEMINI_API_KEY}"
    }},
    storage = {vs_name}.storage_table,
    metadata_columns = ['subject', 'datetime'],
    content_columns = ['body', 'from_field', 'to_field'],
    id_column = 'id';
"""
        
        project.query(create_query).fetch()
        try:
            kb = project.knowledge_bases.get(kb_name)
            logger.info(f"Email knowledge base '{kb.name}' created successfully.")
            return kb
        except Exception as e:
            logger.error("Failed to create email knowledge base.")
            return None
    else:
        logger.info(f"Email knowledge base '{kb_name}' already exists. Skipping creation.")
    
    return project.knowledge_bases.get(kb_name)


def bulk_insert_email_kb(project: Project, kb: KnowledgeBase, db: Database) -> None:
    """
    Bulk insert emails into the knowledge base.
    To be used only when inserting data for the first time.

    Args:
        project (Project): The MindsDB project instance.
        kb (KnowledgeBase): The MindsDB knowledge base instance.
        db (Database): The MindsDB database instance.
    """
    kb_empty_query = f"SELECT * FROM {kb.name} LIMIT 1;"
    res = project.query(kb_empty_query).fetch()

    if not res.empty:
        logger.info(f"Knowledge base '{kb.name}' is not empty. Skipping bulk insert.")
        return

    insert_query = f"""INSERT INTO {kb.name}
SELECT *
FROM {db.name}.emails
LIMIT 100
USING
    kb_no_upsert = true,
    batch_size = 50,
    threads = 1,
    track_column = id;
"""
    
    project.query(insert_query).fetch()
    