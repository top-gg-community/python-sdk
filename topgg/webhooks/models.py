# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from datetime import datetime
from urllib.parse import parse_qsl

from ..models import Platform


class Project:
  """A project."""

  __slots__: tuple[str, ...] = ('id', 'platform', 'platform_id')

  id: int
  """The project's Top.gg ID."""

  platform_id: int
  """The project's Discord client ID or guild ID."""

  platform: Platform
  """The project's platform (always Platform.DISCORD)."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.platform_id = int(json['platform_id'])
    self.platform = Platform(json['platform'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} platform={self.platform!r} platform_id={self.platform_id}>'


class User:
  """A user."""

  __slots__: tuple[str, ...] = ('avatar', 'id', 'name', 'platform_id')

  id: int
  """The user's Top.gg ID."""

  platform_id: int
  """The user's Discord ID."""

  name: str
  """The user's Discord username."""

  avatar: str
  """The user's avatar URL."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.platform_id = int(json['platform_id'])
    self.name = json['name']
    self.avatar = json['avatar_url']

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} name={self.name!r} platform_id={self.platform_id} avatar={self.avatar!r}>'


class VoteCreate:
  """A vote.create webhook payload. Top.gg fires this event each time a user upvotes your project. Use it to reward voters, update leaderboards, or log activity."""

  __slots__: tuple[str, ...] = (
    'created_at',
    'expires_at',
    'id',
    'project',
    'query',
    'user',
    'weight',
  )

  id: int
  """The vote's Top.gg ID."""

  weight: int
  """The vote's weight (1 normally, 2 during weekend multiplier.)"""

  created_at: datetime
  """When the vote was cast."""

  expires_at: datetime
  """When the user can vote again."""

  project: Project
  """The voted project."""

  user: User
  """The voter."""

  query: dict[str, str]
  """The parsed query parameters appended to the /:id/vote page URL."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.weight = json['weight']
    self.created_at = datetime.fromisoformat(json['created_at'].replace('Z', '+00:00'))
    self.expires_at = datetime.fromisoformat(json['expires_at'].replace('Z', '+00:00'))
    self.project = Project(json['project'])
    self.user = User(json['user'])
    self.query = dict(parse_qsl(json['query']))

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} weight={self.weight} project={self.project!r} user={self.user!r} created_at={self.created_at!r} expires_at={self.expires_at!r} query={self.query!r}>'


class Test:
  """A webhook.test webhook payload. This event is always available and lets you verify your endpoint is reachable before real votes arrive. Send a test from your project's Webhooks page in the dashboard."""

  __slots__: tuple[str, ...] = ('project', 'user')

  project: Project
  """The voted project."""

  user: User
  """The voter."""

  def __init__(self, json: dict):
    self.project = Project(json['project'])
    self.user = User(json['user'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} project={self.project!r} user={self.user!r}>'


class IntegrationCreate:
  """A integration.create webhook payload that fires when a user visits your integration page on Top.gg and clicks the Connect button."""

  __slots__: tuple[str, ...] = ('connection_id', 'project', 'user', 'webhook_secret')

  connection_id: int
  """The connection's Top.gg ID. Store this to track and delete."""

  webhook_secret: str
  """The webhook secret (prefixed whs_) used to verify all future webhook."""

  project: Project
  """The connection's project."""

  user: User
  """The connection's user."""

  def __init__(self, json: dict):
    self.connection_id = int(json['connection_id'])
    self.webhook_secret = json['webhook_secret']
    self.project = Project(json['project'])
    self.user = User(json['user'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} connection_id={self.connection_id} webhook_secret={self.webhook_secret!r} project={self.project!r} user={self.user!r}>'


class IntegrationDelete:
  """A integration.delete webhook payload that fires when a user removes the managed webhook from their dashboard."""

  __slots__: tuple[str, ...] = ('connection_id',)

  connection_id: int
  """The connection's Top.gg ID."""

  def __init__(self, json: dict):
    self.connection_id = int(json['connection_id'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} connection_id={self.connection_id}>'
