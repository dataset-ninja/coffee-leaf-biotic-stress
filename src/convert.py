import supervisely as sly
from dataset_tools.convert.coffee.main import to_supervisely

api = sly.Api.from_env()
project_id = to_supervisely(api)

print("Project id is", project_id)


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # * dataset_path = "Path to the local dir with dataset"

    # Function should read local dataset and upload it to Supervisely project, then return project info.

    raise NotImplementedError("The converter should be implemented manually.")

    # * return project
