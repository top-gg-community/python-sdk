# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 null8626 & Top.gg

from typing import TYPE_CHECKING
from datetime import datetime
from enum import Enum

from .util import parse_timestamp

if TYPE_CHECKING:
  from collections.abc import Iterator

  from .client import Client


class UserSource(Enum):
  """A user account from an external platform that is linked to a Top.gg user account."""

  DISCORD = 'discord'
  TOPGG = 'topgg'


class PartialVote:
  """A brief information of a project's vote."""

  __slots__: tuple[str, ...] = ('voted_at', 'expires_at', 'weight')

  voted_at: datetime
  """When the vote was cast."""

  expires_at: datetime
  """When the vote expires and the user is required to vote again."""

  weight: int
  """The number of votes this vote counted for. This is a rounded integer value which determines how many points this individual vote was worth."""

  def __init__(self, json: dict):
    self.voted_at = parse_timestamp(json['created_at'])
    self.expires_at = parse_timestamp(json['expires_at'])
    self.weight = json['weight']

  def __repr__(self) -> str:
    return f'<{__class__.__name__} voted_at={self.voted_at!r} expires_at={self.expires_at!r} weight={self.weight}>'

  def __int__(self) -> int:
    return self.weight


class Vote(PartialVote):
  """A project's vote information."""

  __slots__: tuple[str, ...] = (
    'voter_id',
    'platform_id',
  )

  voter_id: int
  """The voter's ID."""

  platform_id: int
  """The voter's ID on the project's platform."""

  def __init__(self, json: dict):
    super().__init__(json)

    self.voter_id = int(json['user_id'])
    self.platform_id = int(json['platform_id'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} voter_id={self.voter_id} platform_id={self.platform_id} voted_at={self.voted_at!r} expires_at={self.expires_at!r} weight={self.weight}>'

  def __int__(self) -> int:
    return self.weight


class PaginatedVotes:
  """A paginated list of a project's vote information."""

  __slots__: tuple[str, ...] = ('__client', '__votes', '__cursor')

  __client: 'Client'
  __votes: list[Vote]
  __cursor: str

  def __init__(self, client: 'Client', json: dict):
    self.__client = client
    self.__votes = [Vote(vote) for vote in json['data']]
    self.__cursor = json['cursor']

  @property
  def has_next(self) -> bool:
    """Whether there is a next page of votes."""

    return bool(self.__cursor)

  async def next(self) -> 'PaginatedVotes':
    """
    Tries to advance to the next page.

    :exception ValueError: There is no next page.
    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The next page of votes.
    :rtype: :class:`.PaginatedVotes`
    """

    if not self.has_next:
      raise ValueError('There is no next page.')

    return await self.__client._get_votes(cursor=self.__cursor)

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self.__votes!r}>'

  def __len__(self) -> int:
    return len(self.__votes)

  def __iter__(self) -> 'Iterator[Vote]':
    return iter(self.__votes)


class User:
  """A Top.gg user."""

  __slots__: tuple[str, ...] = ('id', 'name', 'avatar_url', 'platform_id')

  id: int
  """The user's ID."""

  name: str
  """The user's name."""

  avatar_url: str
  """The user's avatar URL."""

  platform_id: int
  """The user's platform ID."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.name = json['name']
    self.avatar_url = json['avatar_url']
    self.platform_id = int(json['platform_id'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} name={self.name!r} avatar_url={self.avatar_url!r} platform_id={self.platform_id}>'

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id

