# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 null8626 & Top.gg

from datetime import datetime
from enum import Enum

from .project import PartialProject
from .user import User
from .util import parse_timestamp


class IntegrationCreatePayload:
  """An `integration.create` webhook payload. Fires when a user has connected to your webhook integration."""

  __slots__: tuple[str, ...] = ('connection_id', 'secret', 'project', 'user')

  connection_id: int
  """The unique identifier for this connection."""

  secret: str
  """The secret used to verify future webhook deliveries."""

  project: PartialProject
  """The project that the integration refers to."""

  user: User
  """The user who triggered this event."""

  def __init__(self, json: dict):
    self.connection_id = int(json['connection_id'])
    self.secret = json['webhook_secret']
    self.project = PartialProject(json['project'])
    self.user = User(json['user'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} connection_id={self.connection_id} secret={self.secret!r} project={self.project!r} user={self.user!r}>'

  def __int__(self) -> int:
    return self.connection_id

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.connection_id == other.connection_id


class IntegrationDeletePayload:
  """An `integration.delete` webhook payload. Fires when a user has disconnected from your webhook integration."""

  __slots__: tuple[str, ...] = ('connection_id',)

  connection_id: int
  """The unique identifier for this connection."""

  def __init__(self, json: dict):
    self.connection_id = int(json['connection_id'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} connection_id={self.connection_id}>'

  def __int__(self) -> int:
    return self.connection_id

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.connection_id == other.connection_id


class TestPayload:
  """A `webhook.test` webhook payload. Fires upon sent test from the project dashboard."""

  __slots__: tuple[str, ...] = ('project', 'user')

  project: PartialProject
  """The project that the test refers to."""

  user: User
  """The user who triggered this event."""

  def __init__(self, json: dict):
    self.project = PartialProject(json['project'])
    self.user = User(json['user'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} project={self.project!r} user={self.user!r}>'


class VoteCreatePayload:
  """A `vote.create` webhook payload. Fires when a user votes for your project."""

  __slots__: tuple[str, ...] = (
    'id',
    'weight',
    'voted_at',
    'expires_at',
    'project',
    'user',
  )

  id: int
  """The vote's ID."""

  weight: int
  """The number of votes this vote counted for. This is a rounded integer value which determines how many points this individual vote was worth."""

  voted_at: datetime
  """When the vote was cast."""

  expires_at: datetime
  """When the vote expires and the user is required to vote again."""

  project: PartialProject
  """The project that received this vote."""

  user: User
  """The user who voted for this project."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.weight = json['weight']
    self.voted_at = parse_timestamp(json['created_at'])
    self.expires_at = parse_timestamp(json['expires_at'])
    self.project = PartialProject(json['project'])
    self.user = User(json['user'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} weight={self.weight} voted_at={self.voted_at!r} expires_at={self.expires_at!r} project={self.project!r} user={self.user!r}>'

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


Payload = (
  IntegrationCreatePayload | IntegrationDeletePayload | TestPayload | VoteCreatePayload
)
"""All possible webhook payloads."""


class PayloadType(Enum):
  """A webhook payload's type."""

  INTEGRATION_CREATE = 'integration.create'
  """Fires when a user has connected to your webhook integration."""

  INTEGRATION_DELETE = 'integration.delete'
  """Fires when a user has disconnected from your webhook integration."""

  TEST = 'webhook.test'
  """Fires upon sent test from the project dashboard."""

  VOTE_CREATE = 'vote.create'
  """Fires when a user votes for your project."""

  def _deserialize(self, json: dict) -> Payload:
    cls = None

    match self:
      case self.INTEGRATION_CREATE:
        cls = IntegrationCreatePayload

      case self.INTEGRATION_DELETE:
        cls = IntegrationDeletePayload

      case self.TEST:
        cls = TestPayload

      case self.VOTE_CREATE:
        cls = VoteCreatePayload

    return cls(json)
