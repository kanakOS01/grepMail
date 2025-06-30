import os

from dotenv import load_dotenv
from mindsdb_sdk.projects import Project
from mindsdb_sdk.server import Server
from mindsdb_sdk.models import Model

from grepmail.logger import logger

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


def create_and_get_project(server: Server, project_name: str = "grepmail") -> Project:
    """
    Create a MindsDB project if it doesn't exist, or retrieve it if it does.

    Args:
        server (Server): The MindsDB server instance.
        project_name (str): The name of the project to create or retrieve.
    """
    try:
        project = server.create_project(project_name)
        logger.info(f"Project '{project_name}' created successfully.")
    except Exception:
        project = server.get_project(project_name)
        logger.info(f"Project '{project_name}' already exists. Skipping creation.")
    return project


def create_gemini_engine(server: Server) -> None:
    """
    Create a MindsDB Engine for Gemini if it doesn't exist, or retrieve it if it does.

    Args:
        server (Server): The MindsDB server instance.
    """
    ml_engines = server.ml_engines.list()
    ml_engine_names = [engine.name for engine in ml_engines]
    if 'gemini_engine' in ml_engine_names:
        logger.info("Gemini engine already exists. Skipping creation.")
        return

    query = f"""CREATE ML_ENGINE gemini_engine
FROM google_gemini
USING
    api_key = '{GEMINI_API_KEY}';
    """
    
    try:
        server.query(query).fetch()
        logger.info("Gemini engine created successfully.")
    except Exception as e:
        logger.error(f"Failed to create Gemini engine: {e}")
        raise e


def create_and_get_gist_model(project: Project) -> Model | None:
    """
    Create a MindsDB model for Gist if it doesn't exist, or retrieve it if it does.

    Args:
        project (Project): The MindsDB project instance.
    """
    models = project.models.list()
    model_names = [model.name for model in models]
    if 'gist_generator' in model_names:
        logger.info("Gist model already exists. Skipping creation.")
        return project.get_model('gist_generator')

    query = """CREATE MODEL gist_generator
    PREDICT response
    USING
        engine = 'gemini_engine',
        model_name = 'gemini-2.0-flash',
        prompt_template = 'briefly summarize this email: \n{{email_content}};'
    """

    try:
        project.query(query).fetch()
        logger.info("Gist model created successfully.")
        return project.get_model('gist_generator')
    except Exception as e:
        logger.error(f"Failed to create Gist model: {e}")
        return None


def query_gist_model(project: Project, email_content: str) -> str:
    """
    Query the Gist model to generate a summary of the email content.

    Args:
        project (Project): The MindsDB project instance.
        email_content (str): The content of the email to summarize.

    Returns:
        str: The generated summary.
    """
    query = f"""SELECT response FROM gist_generator
    WHERE email_content = '{email_content}';"""

    try:
        result = project.query(query).fetch()
        return result.to_dict(orient='records')[0]['response']
    except Exception as e:
        logger.error(f"Failed to query Gist model: {e}")
        return "Error generating summary."