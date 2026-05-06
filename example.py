# example.py — theme conflict testing: Python
# Focus: dataclasses, decorators, generators, comprehensions, type hints, property chains

from __future__ import annotations

import asyncio
import functools
import itertools
import json
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Callable, ClassVar, Generator, Generic,
    Iterator, Literal, Optional, TypeVar, overload,
)

# ─── Constants ────────────────────────────────────────────────────────────────

MAX_RETRIES: int   = 3
BASE_URL:    str   = "https://api.example.com"
VERSION:     str   = "1.0.0"
LOG_PATH:    Path  = Path("/var/log/app.log")

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# ─── Enums ───────────────────────────────────────────────────────────────────

class Role(str, Enum):
    ADMIN  = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Theme(Enum):
    LIGHT  = auto()
    DARK   = auto()
    SYSTEM = auto()


class HttpMethod(str, Enum):
    GET    = "GET"
    POST   = "POST"
    PUT    = "PUT"
    DELETE = "DELETE"

# ─── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class SocialLinks:
    twitter: str | None = None
    github:  str | None = None
    website: str | None = None


@dataclass
class UserProfile:
    display_name: str
    bio:          str        = ""
    avatar_url:   str | None = None
    social:       SocialLinks = field(default_factory=SocialLinks)


@dataclass
class UserSettings:
    theme:         Theme = Theme.DARK
    notifications: bool  = True
    language:      str   = "en"


@dataclass
class User:
    id:         int
    username:   str
    email:      str
    role:       Role
    profile:    UserProfile
    settings:   UserSettings  = field(default_factory=UserSettings)
    created_at: datetime      = field(default_factory=datetime.utcnow)

    # property.property.property chain for theme testing ↓
    def describe(self) -> str:
        handle  = self.profile.social.twitter or self.username
        website = self.profile.social.website or "(none)"
        joined  = self.created_at.strftime("%B %Y")
        return f"{self.profile.display_name} (@{handle}) [{self.role.value}] — {website} — {joined}"

    @property
    def contact_info(self) -> dict[str, str | None]:
        return {
            "name":    self.profile.display_name,
            "email":   self.email,
            "twitter": self.profile.social.twitter,
            "github":  self.profile.social.github,
        }

@dataclass
class ApiError:
    code:    str
    message: str
    field:   str | None = None


@dataclass
class ApiResponse(Generic[T]):
    data:   T
    errors: list[ApiError]     = field(default_factory=list)
    meta:   dict[str, Any]     = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def page(self) -> int:
        return self.meta.get("page", 1)

    @property
    def total_pages(self) -> int:
        return self.meta.get("total_pages", 1)

# ─── Decorators ──────────────────────────────────────────────────────────────

def log_call(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"[{func.__name__}] called with args={args!r} kwargs={kwargs!r}")
        result = func(*args, **kwargs)
        print(f"[{func.__name__}] returned {result!r}")
        return result
    return wrapper


def retry(times: int = MAX_RETRIES, exceptions: tuple = (Exception,)):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == times:
                        raise
                    print(f"Retry {attempt}/{times} after error: {exc}")
        return wrapper
    return decorator


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email))

# ─── Abstract Base ───────────────────────────────────────────────────────────

class Repository(ABC, Generic[T]):
    _items: ClassVar[dict]

    @abstractmethod
    def find(self, id: int) -> T | None: ...

    @abstractmethod
    def save(self, item: T) -> int: ...

    @abstractmethod
    def delete(self, id: int) -> None: ...

    @abstractmethod
    def all(self) -> list[T]: ...

# ─── Concrete Repository ─────────────────────────────────────────────────────

class InMemoryUserRepo(Repository[User]):
    def __init__(self) -> None:
        self._store:   dict[int, User] = {}
        self._next_id: int             = 1

    def find(self, id: int) -> User | None:
        return self._store.get(id)

    def save(self, user: User) -> int:
        if user.id == 0:
            user.id = self._next_id
            self._next_id += 1
        self._store[user.id] = user
        return user.id

    def delete(self, id: int) -> None:
        if id not in self._store:
            raise KeyError(f"User {id} not found")
        del self._store[id]

    def all(self) -> list[User]:
        return list(self._store.values())

    def by_role(self, role: Role) -> list[User]:
        return [u for u in self._store.values() if u.role == role]

# ─── Service class ───────────────────────────────────────────────────────────

class UserService:
    def __init__(self, repo: InMemoryUserRepo) -> None:
        self._repo   = repo
        self._cache: dict[int, User] = {}

    @log_call
    def create_user(
        self,
        username: str,
        email:    str,
        role:     Role = Role.VIEWER,
        *,
        display_name: str = "",
        github:       str | None = None,
        twitter:      str | None = None,
    ) -> User:
        if not validate_email(email):
            raise ValueError(f"Invalid email: {email!r}")

        user = User(
            id         = 0,
            username   = username,
            email      = email,
            role       = role,
            profile    = UserProfile(
                display_name = display_name or username,
                social       = SocialLinks(github=github, twitter=twitter),
            ),
        )
        self._repo.save(user)
        return user

    def get_user(self, id: int) -> User:
        if id in self._cache:
            return self._cache[id]
        user = self._repo.find(id)
        if user is None:
            raise LookupError(f"User {id} not found")
        self._cache[id] = user
        return user

    # Deep property chain access
    def summarise_users(self) -> list[str]:
        return [
            f"{u.profile.display_name} <{u.email}> [{u.role.value}] "
            f"gh={u.profile.social.github or '-'} "
            f"tw={u.profile.social.twitter or '-'}"
            for u in self._repo.all()
        ]

    def group_by_role(self) -> dict[Role, list[User]]:
        result: dict[Role, list[User]] = defaultdict(list)
        for user in self._repo.all():
            result[user.role].append(user)
        return dict(result)

    def update_settings(self, id: int, **kwargs: Any) -> User:
        user = self.get_user(id)
        for key, val in kwargs.items():
            if hasattr(user.settings, key):
                setattr(user.settings, key, val)
        self._repo.save(user)
        return user

# ─── Generators & Comprehensions ─────────────────────────────────────────────

def fibonacci() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def paginate(items: list[T], per_page: int = 10) -> Iterator[list[T]]:
    for i in range(0, len(items), per_page):
        yield items[i : i + per_page]


def flatten(nested: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(nested))


def word_frequency(text: str) -> dict[str, int]:
    words = text.lower().split()
    freq: dict[str, int] = defaultdict(int)
    for word in words:
        freq[word] += 1
    return dict(sorted(freq.items(), key=lambda kv: kv[1], reverse=True))


matrix_transpose = lambda m: [[row[i] for row in m] for i in range(len(m[0]))]

# Dict comprehensions / nested comprehensions
def build_permission_map(roles: list[Role]) -> dict[str, list[str]]:
    permissions = {
        Role.ADMIN:  ["read", "write", "delete", "admin"],
        Role.EDITOR: ["read", "write"],
        Role.VIEWER: ["read"],
    }
    return {
        role.value: [
            perm.upper()
            for perm in permissions.get(role, [])
        ]
        for role in roles
    }

# ─── Async ───────────────────────────────────────────────────────────────────

async def fetch_user(session: Any, user_id: int) -> dict:
    async with session.get(f"{BASE_URL}/users/{user_id}") as resp:
        resp.raise_for_status()
        return await resp.json()


async def fetch_all_users(user_ids: list[int]) -> list[dict]:
    # Simulated — no real aiohttp dependency
    results = await asyncio.gather(
        *[asyncio.sleep(0, result={"id": uid, "name": f"user_{uid}"}) for uid in user_ids],
        return_exceptions=True,
    )
    return [r for r in results if not isinstance(r, Exception)]

# ─── Context Manager ─────────────────────────────────────────────────────────

class Timer:
    def __init__(self, label: str) -> None:
        self.label     = label
        self.elapsed   = 0.0
        self._start: float

    def __enter__(self) -> "Timer":
        import time
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> Literal[False]:
        import time
        self.elapsed = time.perf_counter() - self._start
        print(f"{self.label}: {self.elapsed * 1000:.2f}ms")
        return False

# ─── Overloads ───────────────────────────────────────────────────────────────

@overload
def coerce(value: str) -> str: ...
@overload
def coerce(value: int) -> int: ...
@overload
def coerce(value: float) -> float: ...

def coerce(value):  # type: ignore[misc]
    return value

# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Forest Phosphor theme test — Python — v{VERSION}")
    print(f"Log path: {LOG_PATH}")

    repo    = InMemoryUserRepo()
    service = UserService(repo)

    alice = service.create_user(
        "alice", "alice@example.com", Role.ADMIN,
        display_name="Alice Forester",
        github="alice-dev",
        twitter="@alice",
    )
    bob = service.create_user(
        "bob", "bob@example.com", Role.EDITOR,
        display_name="Bob Treewright",
    )
    _ = service.create_user("carol", "carol@example.com")

    print(alice.describe())
    print(bob.contact_info)

    for summary in service.summarise_users():
        print(summary)

    grouped = service.group_by_role()
    for role, users in grouped.items():
        print(f"{role.value}: {[u.username for u in users]}")

    service.update_settings(alice.id, theme=Theme.LIGHT, language="fr")
    updated = service.get_user(alice.id)
    print(f"Alice theme: {updated.settings.theme}, lang: {updated.settings.language}")

    perm_map = build_permission_map(list(Role))
    print(json.dumps(perm_map, indent=2))

    fib10 = list(itertools.islice(fibonacci(), 10))
    print("Fibonacci:", fib10)

    items = list(range(23))
    for page in paginate(items, per_page=8):
        print("Page:", page)

    freq = word_frequency("the quick brown fox jumps over the lazy dog the fox the")
    print("Top word:", next(iter(freq)))

    m = [[1, 2, 3], [4, 5, 6]]
    print("Transposed:", matrix_transpose(m))

    with Timer("sleep"):
        import time; time.sleep(0.01)

    users_data = asyncio.run(fetch_all_users([1, 2, 3]))
    print("Fetched:", users_data)


if __name__ == "__main__":
    main()
