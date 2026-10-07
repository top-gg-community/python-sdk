# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 null8626 & Top.gg

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .util import parse_timestamp, safe_dict


class Platform(Enum):
  """A project's platform."""

  DISCORD = 'discord'
  ROBLOX = 'roblox'


class ProjectType(Enum):
  """A project's type."""

  BOT = 'bot'
  SERVER = 'server'
  GAME = 'game'


class PartialProject:
  """A brief information on a project listed on Top.gg."""

  __slots__: tuple[str, ...] = ('id', 'type', 'platform', 'platform_id')

  id: int
  """The project's ID."""

  type: ProjectType
  """The project's type."""

  platform: Platform
  """The project's platform."""

  platform_id: int
  """The project's platform ID."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.type = ProjectType(json['type'])
    self.platform = Platform(json['platform'])
    self.platform_id = int(json['platform_id'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} type={self.type!r} platform={self.platform!r} platform_id={self.platform_id}>'

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


class Project:
  """A project listed on Top.gg."""

  __slots__: tuple[str, ...] = (
    'id',
    'name',
    'platform',
    'type',
    'headline',
    'tags',
    'current_votes',
    'total_votes',
    'review_score',
    'review_count',
  )

  id: int
  """The project's ID."""

  name: str
  """The project's name sourced from the external platform."""

  platform: Platform
  """The project's platform."""

  type: ProjectType
  """The project's type."""

  headline: str
  """The project's short description."""

  tags: list[str]
  """The project's tag IDs."""

  current_votes: int
  """The project's current vote count that affects the project's ranking."""

  total_votes: int
  """The project's total vote count."""

  review_score: float
  """The project's review score out of 5."""

  review_count: int
  """The project's total review count."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.name = json['name']
    self.platform = Platform(json['platform'])
    self.type = ProjectType(json['type'])
    self.headline = json['headline']
    self.tags = json['tags']
    self.current_votes = json['votes']
    self.total_votes = json['votes_total']
    self.review_score = json['review_score']
    self.review_count = json['review_count']

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} name={self.name!r} type={self.type!r} platform={self.platform!r} headline={self.headline!r} current_votes={self.current_votes} total_votes={self.total_votes} review_score={self.review_score!r}>'

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


class Announcement:
  """A project's announcement."""

  __slots__: tuple[str, ...] = ('title', 'content', 'created_at')

  title: str
  """The announcement's title."""

  content: str
  """The announcement's content."""

  created_at: datetime
  """When the announcement was created."""

  def __init__(self, json: dict):
    self.title = json['title']
    self.content = json['content']
    self.created_at = parse_timestamp(json['created_at'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} title={self.title!r} content={self.content!r}>'


@dataclass(frozen=True, repr=False, slots=True)
class Metrics:
  """A project metrics."""

  _json: dict

  @staticmethod
  def discord_bot(
    server_count: int | None = None, shard_count: int | None = None
  ) -> 'Metrics':
    """Creates a new Discord bot metrics."""

    if server_count is None and shard_count is None or not (
      isinstance(server_count, int) or isinstance(shard_count, int)
    ):
      raise TypeError(
        'The specified server count and/or shard count must be an integer.'
      )

    return Metrics(safe_dict(server_count=server_count, shard_count=shard_count))

  @staticmethod
  def discord_server(
    member_count: int | None = None, online_count: int | None = None
  ) -> 'Metrics':
    """Creates a new Discord server metrics."""

    if member_count is None and online_count is None or not (
      isinstance(member_count, int) or isinstance(online_count, int)
    ):
      raise TypeError(
        'The specified member count and/or online count must be an integer.'
      )

    return Metrics(safe_dict(member_count=member_count, online_count=online_count))

  @staticmethod
  def roblox_game(player_count: int) -> 'Metrics':
    """Creates a new Roblox game metrics."""

    if not isinstance(player_count, int):
      raise TypeError('The specified player count must be an integer.')

    return Metrics(safe_dict(player_count=player_count))
