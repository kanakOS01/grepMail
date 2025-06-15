from mindsdb_sdk.projects import Project
from mindsdb_sdk.server import Server

from grepmail.logger import logger


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
