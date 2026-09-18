from collections.abc import Coroutine, Callable

from app.models import User, Post, Vote
from app.schemas import tokens

type UserCreator = Callable[[str, str], Coroutine[None, None, tuple[User, str]]]
type TokenCreator = Callable[[str, str], Coroutine[None, None, tokens.Token]]
type PostCreator = Callable[[User], Coroutine[None, None, Post]]
type VoteCreator = Callable[[User, Post], Coroutine[None, None, Vote]]
