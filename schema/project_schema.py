from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.project import Project


class ProjectSchema:

    def __init__(self, project: 'Project'):
        self.project: Project = project
