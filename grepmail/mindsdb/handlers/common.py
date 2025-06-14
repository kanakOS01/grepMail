import mindsdb_sdk
from mindsdb_sdk.projects import Project
from mindsdb_sdk.server import Server


def create_and_get_project(server: Server, project_name: str = "grepmail") -> Project:
    try:
        project = server.create_project(project_name)
    except Exception:
        project = server.get_project(project_name)
    return project
