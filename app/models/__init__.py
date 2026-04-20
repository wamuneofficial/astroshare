# Экспортируем все модели из одного места.
# Благодаря этому в других файлах можно писать:
#   from app.models import User
# вместо:
#   from app.models.user import User

from .user import User
from .photo import Photo, Like
from .comment import Comment
from .news import News
from .notification import Notification
from .post import Post
from .message import Message
from .friendship import Friendship
from .material import Material
from .groupchat import GroupChat, GroupChatMember, GroupChatMessage
