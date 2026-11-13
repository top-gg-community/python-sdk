# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import UTC, datetime
from enum import Enum


class Platform(Enum):
  """A project's platform."""

  __slots__: tuple[str, ...] = ()

  DISCORD = 'discord'
  """Discord."""

  ROBLOX = 'roblox'
  """Roblox."""


class ProjectType(Enum):
  """A project's type."""

  __slots__: tuple[str, ...] = ()

  BOT = 'bot'
  """A bot."""

  SERVER = 'server'
  """A server."""

  GAME = 'game'
  """A game."""


class Model(ABC):
  """A base API object."""

  __slots__: tuple[str, ...] = ()

  @abstractmethod
  def __init__(self, json: dict):
    pass


class PartialProject(Model):
  """A partial project."""

  __slots__: tuple[str, ...] = ('id', 'name', 'platform', 'platform_id', 'type')

  id: int
  """The project's Top.gg ID."""

  platform_id: int
  """The project's platform ID."""

  name: str
  """The project's name in its platform."""

  platform: Platform
  """The project's platform."""

  type: ProjectType
  """The project's type."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.platform_id = int(json['platform_id'])
    self.name = json['name']
    self.platform = Platform(json['platform'])
    self.type = ProjectType(json['type'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} type={self.type!r} name={self.name!r} platform={self.platform!r} platform_id={self.platform_id}>'

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


class Project(Model):
  """A project."""

  __slots__: tuple[str, ...] = (
    'current_votes',
    'headline',
    'id',
    'name',
    'platform',
    'review_count',
    'review_score',
    'tags',
    'total_votes',
    'type',
  )

  id: int
  """The project's Top.gg ID."""

  name: str
  """The project's name in its platform."""

  platform: Platform
  """The project's platform."""

  type: ProjectType
  """The project's type."""

  headline: str
  """The project's headline."""

  tags: list[str]
  """The project's tags."""

  current_votes: int
  """The project's current vote count."""

  total_votes: int
  """The project's vote count."""

  review_score: float
  """The project's review score."""

  review_count: int
  """The project's review count."""

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
    return f'<{__class__.__name__} id={self.id} type={self.type!r} name={self.name!r} platform={self.platform!r} tags={self.tags!r} current_votes={self.current_votes} total_votes={self.total_votes} review_score={self.review_score!r} review_count={self.review_count}>'

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


class Locale(Enum):
  """A supported locale."""

  __slots__: tuple[str, ...] = ()

  ENGLISH = 'en'
  """English."""

  GERMAN = 'de'
  """German."""

  FRENCH = 'fr'
  """French."""

  PORTUGUESE = 'pt'
  """Portuguese."""

  TURKISH = 'tr'
  """Turkish."""

  HINDI = 'hi'
  """Hindi."""

  JAPANESE = 'ja'
  """Japanese."""

  ARABIC = 'ar'
  """Arabic."""

  DUTCH = 'nl'
  """Dutch."""

  KOREAN = 'ko'
  """Korean."""

  ITALIAN = 'it'
  """Italian."""

  SPANISH = 'es'
  """Spanish."""

  RUSSIAN = 'ru'
  """Russian."""

  UKRAINIAN = 'uk'
  """Ukrainian."""

  VIETNAMESE = 'vi'
  """Vietnamese."""

  CHINESE_SIMPLIFIED = 'zh'
  """Chinese Simplified."""


class LocaleMap:
  """
  A locale-text map.

  :param data: The data. Defaults to :py:obj:`None`.
  :type data: :py:class:`dict`[:class:`.Locale`, :py:class:`str`] | :py:obj:`None`
  """

  __slots__: tuple[str, ...] = ('_json',)

  _json: dict

  def __init__(self, data: dict[Locale, str] | None = None):
    self._json = {}

    if data is not None:
      for key, value in data.items():
        self[key] = value

  def _enforce_constraints(self, minimum: int, maximum: int) -> None:
    for value in self._json.values():
      if len(value) < minimum:
        raise ValueError('A LocaleMap text length is below the minimum threshold.')
      elif len(value) > maximum:
        raise ValueError('A LocaleMap text length is above the maximum threshold.')

  def __setitem__(self, locale: Locale, text: str) -> None:
    """
    Inserts a new locale-text entry.

    :param locale: The locale.
    :type locale: :class:`.Locale`
    :param text: The text.
    :type text: :class:`str`

    :exception TypeError: ``locale`` is not a part of the :class:`.Locale` enum or ``text`` is not a :class:`str`.
    """

    if not isinstance(locale, Locale):
      raise TypeError('The specified locale must be a Locale.')
    elif not isinstance(text, str):
      raise TypeError('The specified locale must be a string.')

    self._json[locale.value] = text

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self._json!r}>'


class AnnouncementCategory(Enum):
  """An announcement category."""

  __slots__: tuple[str, ...] = ()

  ANNOUNCEMENT = 'announcement'
  """A generic announcement."""

  EVENT = 'event'
  """An event."""

  NEW_FEATURE = 'new_feature'
  """A new feature."""


class Metrics(ABC):
  """A project's metrics."""

  __slots__: tuple[str, ...] = ()

  @abstractmethod
  def _to_json(self) -> dict:
    pass


class DiscordBotMetrics(Metrics):
  """
  A Discord bot's metrics.

  :param server_count: The bot's server count.
  :type server_count: :class:`int`
  :param shard_count: The bot's shard count.
  :type shard_count: :class:`int`

  :exception TypeError: ``server_count`` is not a :class:`int` or ``shard_count`` is not a :class:`int`.
  :exception ValueError: The ``server_count`` and/or ``shard_count`` must be specified.
  """

  __slots__: tuple[str, ...] = ('server_count', 'shard_count')

  server_count: int | None
  shard_count: int | None

  def __init__(self, *, server_count: int | None = None, shard_count: int | None = None):
    if server_count is None and shard_count is None:
      raise ValueError('The server count and/or shard count must be specified.')
    elif server_count is not None and not isinstance(server_count, int):
      raise TypeError('The specified server count must be an integer.')
    elif shard_count is not None and not isinstance(shard_count, int):
      raise TypeError('The specified shard count must be an integer.')

    self.server_count = server_count
    self.shard_count = shard_count

  def __repr__(self) -> str:
    return f'<{__class__.__name__} server_count={self.server_count} shard_count={self.shard_count}>'

  def _to_json(self) -> dict:
    json = {}

    if self.server_count is not None:
      json['server_count'] = self.server_count
    if self.shard_count is not None:
      json['shard_count'] = self.shard_count

    return json


class DiscordServerMetrics(Metrics):
  """
  A Discord server's metrics.

  :param total_member_count: The server's server count.
  :type total_member_count: :class:`int`
  :param online_member_count: The server's shard count.
  :type online_member_count: :class:`int`

  :exception TypeError: ``online_member_count`` is not a :class:`int` or ``online_member_count`` is not a :class:`int`.
  :exception ValueError: The ``online_member_count`` and/or ``online_member_count`` must be specified.
  """

  __slots__: tuple[str, ...] = ('online_member_count', 'total_member_count')

  total_member_count: int | None
  online_member_count: int | None

  def __init__(self, *, total_member_count: int | None = None, online_member_count: int | None = None):
    if total_member_count is None and online_member_count is None:
      raise ValueError('The total member count and/or online member count must be specified.')
    elif total_member_count is not None and not isinstance(total_member_count, int):
      raise TypeError('The specified total member count must be an integer.')
    elif online_member_count is not None and not isinstance(online_member_count, int):
      raise TypeError('The specified online member count must be an integer.')

    self.total_member_count = total_member_count
    self.online_member_count = online_member_count

  def __repr__(self) -> str:
    return f'<{__class__.__name__} total_member_count={self.total_member_count} online_member_count={self.online_member_count}>'

  def _to_json(self) -> dict:
    json = {}

    if self.total_member_count is not None:
      json['total_member_count'] = self.total_member_count
    if self.online_member_count is not None:
      json['online_member_count'] = self.online_member_count

    return json


class RobloxGameMetrics(Metrics):
  """
  A Roblox game's metrics.

  :param player_count: The game's current player count.
  :type player_count: :class:`int`

  :exception TypeError: ``player_count`` is not a :class:`int`.
  """

  __slots__: tuple[str, ...] = ('player_count',)

  player_count: int

  def __init__(self, player_count: int):
    if not isinstance(player_count, int):
      raise TypeError('The specified player count must be an integer.')

    self.player_count = player_count

  def __repr__(self) -> str:
    return f'<{__class__.__name__} player_count={self.player_count}>'

  def _to_json(self) -> dict:
    return {'player_count': self.player_count}


class TimestampedMetrics[M: Metrics]:
  """A project's timestamped metrics."""

  __slots__: tuple[str, ...] = ('_json',)

  _json: list[dict]

  def __init__(self):
    self._json = []

  def __repr__(self) -> str:
    return f'<{__class__.__name__} [{", ".join(f"{entry['timestamp']!r} => {entry['metrics']!r}" for entry in self._json)}]>'

  def __len__(self) -> int:
    return len(self._json)

  def add(self, timestamp: datetime, metrics: M) -> None:
    """
    Inserts a new timestamped metrics entry.

    :param timestamp: The timestamp.
    :type timestamp: :class:`datetime`
    :param metrics: The project's metrics.
    :type metrics: :class:`.Metrics`

    :exception TypeError: ``timestamp`` is not a :class:`datetime` or ``metrics`` is not a :class:`.Metrics`.
    """

    if not isinstance(timestamp, datetime):
      raise TypeError('The specified timestamp must be a datetime.')
    elif not isinstance(metrics, Metrics):
      raise TypeError('The specified metrics must be a child of Metrics.')

    self._json.append(
      {
        'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'metrics': metrics._to_json(),
      }
    )

  def clear(self) -> None:
    """Clears all timestamped metrics entries."""

    self._json.clear()


class PartialVote(Model):
  """A partial vote."""

  __slots__: tuple[str, ...] = ('created_at', 'expires_at', 'weight')

  weight: int
  """The vote's weight (1 normally, 2 during weekend multiplier.)"""

  created_at: datetime
  """When the vote was cast."""

  expires_at: datetime
  """When the user can vote again."""

  @property
  def has_expired(self) -> bool:
    """Whether the vote has expired."""

    return datetime.now(UTC) >= self.expires_at

  def __init__(self, json: dict):
    self.weight = json['weight']
    self.created_at = datetime.fromisoformat(json['created_at'].replace('Z', '+00:00'))
    self.expires_at = datetime.fromisoformat(json['expires_at'].replace('Z', '+00:00'))

  def __repr__(self) -> str:
    return f'<{__class__.__name__} weight={self.weight} created_at={self.created_at!r} expires_at={self.expires_at!r}>'


class UserSource(Enum):
  """A user's source platform."""

  __slots__: tuple[str, ...] = ()

  TOPGG = 'topgg'
  """The user came from Top.gg"""

  DISCORD = 'discord'
  """The user came from Discord."""


class Vote(PartialVote):
  """A vote."""

  __slots__: tuple[str, ...] = ('platform_id', 'user_id')

  user_id: int
  """The voter's Top.gg ID."""

  platform_id: int
  """The voter's platform ID."""

  def __init__(self, json: dict):
    super().__init__(json)

    self.user_id = int(json['user_id'])
    self.platform_id = int(json['platform_id'])

  def __repr__(self) -> str:
    return (
      f'<{__class__.__name__} user_id={self.user_id} platform_id={self.platform_id}>'
    )


class Integration(Model):
  """An integration."""

  __slots__: tuple[str, ...] = ('connected', 'description', 'icon_url', 'id', 'name')

  id: int
  """The integration's Top.gg ID."""

  name: str
  """The integration's name."""

  description: str
  """The integration's description."""

  icon_url: str
  """The integration's icon URL."""

  connected: bool
  """Whether the integration is connected to the project."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.name = json['name']
    self.description = json['description']
    self.icon_url = json['icon_url']
    self.connected = json['connected']

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} name={self.name!r} description={self.description!r} connected={self.connected} icon_url={self.icon_url!r}>'

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


class BaseWebhook(Model):
  """A base webhook."""

  __slots__: tuple[str, ...] = ('label', 'url')

  label: str
  """The webhook's label."""

  url: str
  """The webhook's URL."""

  def __init__(self, json: dict):
    self.label = json['label']
    self.url = json['url']

  def __repr__(self) -> str:
    return f'<{__class__.__name__} label={self.label!r} url={self.url!r}>'


class Webhook(BaseWebhook):
  """A webhook."""

  __slots__: tuple[str, ...] = ('id',)

  id: int
  """The webhook's Top.gg ID."""

  def __init__(self, json: dict):
    super().__init__(json)

    self.id = int(json['id'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id}>'

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


class UserConnection(Model):
  """A user's platform connection."""

  __slots__: tuple[str, ...] = ('id', 'platform')

  platform: Platform
  """The connection's platform."""

  id: int
  """The user's platform ID."""

  def __init__(self, json: dict):
    self.platform = Platform(json['platform'])
    self.id = int(json['id'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} platform={self.platform!r}>'

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


class User(Model):
  """A user."""

  __slots__: tuple[str, ...] = ('avatar', 'connections', 'id', 'username')

  id: int
  """The user's Top.gg ID."""

  username: str
  """The user's username."""

  avatar: str | None
  """The user's avatar URL."""

  connections: list[UserConnection]
  """The user's platform connections."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.username = json['username']
    self.avatar = json.get('avatar')
    self.connections = [
      UserConnection(connection) for connection in json['connections']
    ]

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} username={self.username!r} avatar={self.avatar!r} connections={self.connections!r}>'

  def __eq__(self, other: object) -> bool:
    return isinstance(other, __class__) and self.id == other.id


class ReviewStatus(Enum):
  """A project's review status."""

  __slots__: tuple[str, ...] = ()

  DRAFT = 'draft'
  """The project is currently a draft."""

  IN_REVIEW = 'in_review'
  """The project is currently in the reviewer queue."""

  APPROVED = 'approved'
  """The project is approved and listed."""


class UserProject(PartialProject):
  """A user's project."""

  __slots__: tuple[str, ...] = ('headline', 'review_status')

  headline: str
  """The project's headline."""

  review_status: ReviewStatus
  """The project's review status."""

  def __init__(self, json: dict):
    super().__init__(json)

    self.headline = json['headline']
    self.review_status = ReviewStatus(json['review_status'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} headline={self.headline!r} review_status={self.review_status!r}>'


class ProjectSubmission(Model):
  """A project submission."""

  __slots__: tuple[str, ...] = (
    'headline',
    'page_content',
    'platform',
    'platform_id',
    'type',
  )

  platform: Platform
  """The project's platform."""

  type: ProjectType
  """The project's type."""

  platform_id: int
  """The project's platform ID."""

  headline: str
  """The project's headline."""

  page_content: str
  """The project's page content."""

  def __init__(self, json: dict):
    self.platform = Platform(json['platform'])
    self.type = ProjectType(json['type'])
    self.platform_id = int(json['platform_id'])
    self.headline = json['headline']
    self.page_content = json['page_content']

  def __repr__(self) -> str:
    return f'<{__class__.__name__} headline={self.headline!r} page_content={self.page_content!r} platform={self.platform!r} platform_id={self.platform_id} type={self.type!r}>'


class Paginated[T: Model]:
  """An API call result that may contain paginated data."""

  __slots__: tuple[str, ...] = ('_cursor', '_data')

  _data: list[T]
  _cursor: str | None

  def __init__(self, cls: type[T], key: str, json: dict):
    self._data = [cls(data) for data in json[key]]
    self._cursor = json.get('cursor')

  def __len__(self) -> int:
    return len(self._data)

  def __iter__(self) -> Iterator[T]:
    return iter(self._data)

  def __repr__(self) -> str:
    return f'<{__class__.__name__} [{len(self)}]>'