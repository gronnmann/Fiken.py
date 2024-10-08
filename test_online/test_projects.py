import random

from fiken_py.models import Project


def get_or_create_project(unique_id) -> Project:
    projects = Project.getAll()

    found = False
    for project in projects:
        if project.name == f"Test project ({unique_id})":
            found = True
            print(f"Found project {project.projectId}")
            break

    if not found:
        project_request = Project(
            name=f"Test project ({unique_id})",
            startDate="2021-01-01",
            number=unique_id,
        )

        project = project_request.save()

    return project


def test_create_project(unique_id):
    project = get_or_create_project(unique_id)

    assert project is not None
    assert project.name == f"Test project ({unique_id})"


def test_get_projects():
    projects = Project.getAll()

    assert projects is not None
    assert len(projects) > 0


def test_get_single_project(unique_id):
    test_project = get_or_create_project(unique_id)

    project: Project = Project.get(projectId=test_project.projectId)

    assert project is not None
    assert project.projectId == test_project.projectId
    assert project.name == f"Test project ({unique_id})"


def test_patch_single_project(unique_id):
    test_project = get_or_create_project(unique_id)

    project: Project = Project.get(projectId=test_project.projectId)
    assert project.completed is False
    project.completed = True
    project.save()

    assert project.completed is True

    project: Project = Project.get(projectId=test_project.projectId)

    assert project.completed is True


def test_delete_single_project(unique_id):
    test_project = get_or_create_project(unique_id)

    project: Project = Project.get(projectId=test_project.projectId)

    assert Project is not None

    project.delete()

    project: Project = Project.get(projectId=test_project.projectId)

    assert project is None
