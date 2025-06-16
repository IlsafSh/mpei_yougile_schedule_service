"""
Инициализация ресурсных модулей.
"""

from .auth import AuthResource
from .boards import BoardsResource
from .chat_messages import ChatMessagesResource
from .columns import ColumnsResource
from .departments import DepartmentsResource
from .employees import EmployeesResource
from .companies import CompaniesResource
from .files import FilesResource
from .group_chats import GroupChatsResource
from .project_roles import ProjectRolesResource
from .projects import ProjectsResource
from .sprint_sticker_states import SprintStickerStatesResource
from .sprint_stickers import SprintStickersResource
from .string_stickers import StringStickersResource
from .string_sticker_states import StringStickerStatesResource
from .tasks import TasksResource
from .webhooks import WebhooksResource

__all__ = [
    'AuthResource',
    'BoardsResource',
    'ChatMessagesResource',
    'ColumnsResource',
    'DepartmentsResource',
    'EmployeesResource',
    'GroupChatsResource',
    'ProjectRolesResource',
    'ProjectsResource',
    'SprintStickerStatesResource',
    'SprintStickersResource',
    'StringStickersResource',
    'StringStickerStatesResource',
    'TasksResource',
    'WebhooksResource'
]
