import mindsdb_sdk


class Base():
    def __init__(
            self, 
            mindsdb_server_url: str = "http://127.0.0.1:47334", 
            project_name: str = "grepmail"
        ):
        self.server = mindsdb_sdk.connect(mindsdb_server_url)

        # create project if not present
        try:
            self.project = self.server.get_project(project_name)
        except Exception:
            self.project = self.server.create_project(project_name)

        