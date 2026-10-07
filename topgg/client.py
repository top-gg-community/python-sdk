# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from typing import TYPE_CHECKING
from datetime import datetime
from asyncio import sleep
from time import time
from re import sub
import json

if TYPE_CHECKING:
  from typing import Any
  from yarl import Query

from .user import PaginatedVotes, PartialVote, UserSource
from .errors import Error, Ratelimited, RequestError
from .project import Announcement, Metrics, Project
from .util import insert_locale_mapping
from .ratelimiter import Ratelimiter
from .version import VERSION
from .locale import Locale


API_VERSION = 'v1'
BASE_URL = f'https://top.gg/api/{API_VERSION}'
MAXIMUM_DELAY_THRESHOLD = 5.0


class Client:
  """
  Interact with Top.gg API v1's endpoints.

  :param token: The API token to use.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None` (creates a new one instead)
  :type session: :class:`~aiohttp.ClientSession` | :py:obj:`None`

  :exception TypeError: The specified token is not a string.
  :exception ValueError: The specified token is empty.
  """

  __slots__: tuple[str, ...] = (
    '__own_session',
    '__session',
    '__token',
    '__ratelimiters',
    '__current_ratelimits',
  )

  __own_session: bool
  __session: ClientSession
  __token: str
  __ratelimiters: dict[str, Ratelimiter]
  __current_ratelimits: dict[str, float | None]

  def __init__(self, token: str, *, session: ClientSession | None = None):
    if not isinstance(token, str):
      raise TypeError('An API token is required to use this API.')
    elif not token:
      raise ValueError('An API token is required to use this API.')

    self.__own_session = session is None
    self.__session = session or ClientSession(
      timeout=ClientTimeout(total=MAXIMUM_DELAY_THRESHOLD)
    )
    self.__token = token

    endpoint_ratelimits = {
      'projects_@me': Ratelimiter(99),
      'projects_@me_announcements': Ratelimiter(1, 14400),
      'projects_@me_commands': Ratelimiter(99),
      'projects_@me_metrics': Ratelimiter(99),
      'projects_@me_metrics_batch': Ratelimiter(99),
      'projects_@me_votes_number': Ratelimiter(99),
      'projects_@me_votes': Ratelimiter(99),
    }

    self.__ratelimiters = endpoint_ratelimits
    self.__current_ratelimits = {key: None for key in endpoint_ratelimits.keys()}

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self.__session!r}>'

  async def __request(
    self, method: str, path: str, *, params: 'Query' = None, body: 'Any' = None
  ) -> 'Any':
    if self.__session.closed:
      raise Error('Client session is already closed.')

    ratelimiter_key = sub(
      '_{2,}', '_', sub(r'\d+', 'number', path).strip('/').replace('/', '_')
    )

    current_ratelimit = self.__current_ratelimits[ratelimiter_key]

    if current_ratelimit is not None:
      current_time = time()

      if current_time < current_ratelimit:
        raise Ratelimited(current_ratelimit - current_time)
      else:  # pragma: nocover
        self.__current_ratelimits[ratelimiter_key] = None

    ratelimiter = self.__ratelimiters[ratelimiter_key]

    kwargs = {}

    if params is not None:
      kwargs['params'] = params

    if body is not None:
      kwargs['data'] = json.dumps(body)

    max_retries = 3
    retries = 0

    while True:
      status = None
      retry_after = 0.0
      output = None

      async with ratelimiter:
        try:
          async with self.__session.request(
            method,
            BASE_URL + path,
            headers={
              'Authorization': f'Bearer {self.__token}',
              'Content-Type': 'application/json',
              'User-Agent': f'topggpy (https://github.com/top-gg-community/python-sdk {VERSION}) Python/',
            },
            **kwargs,
          ) as resp:
            status = resp.status

            try:
              try:
                output = await resp.json()
              except:
                pass

              retry_after = float(resp.headers.get('Retry-After', 0))
            except (ValueError, json.decoder.JSONDecodeError):  # pragma: nocover
              pass

            resp.raise_for_status()

            return output
        except ClientResponseError:
          if status == 429 and retry_after is not None:
            if retry_after > MAXIMUM_DELAY_THRESHOLD:
              self.__current_ratelimits[ratelimiter_key] = time() + retry_after

              raise Ratelimited(retry_after) from None
            else:  # pragma: nocover
              retries += 1

              if retries >= max_retries:
                raise Ratelimited(retry_after) from None

              await sleep(retry_after)

              continue

          raise RequestError(output and output.get('detail', output), status) from None

  async def get_self(self) -> Project:
    """
    Tries to get your project's information.

    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: Your project's information.
    :rtype: :class:`.Project`
    """

    return Project(await self.__request('GET', '/projects/@me'))

  async def edit_self(
    self, *, headline: dict[Locale, str] = {}, content: dict[Locale, str] = {}
  ) -> None:
    """
    Tries to update your project's information.

    :param headline: A locale mapping of your project's headline.
    :type headline: dict[:class:`.Locale`, :py:class:`str`]
    :param content: A locale mapping of your project's page content.
    :type content: dict[:class:`.Locale`, :py:class:`str`]

    :exception Error: The client is already closed.
    :exception TypeError: The headline and/or content's keys are not an instance of :class:`.Locale`.
    :exception ValueError: The headline and content are left unspecified.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.
    """

    body = {}

    if headline:
      insert_locale_mapping('headline', headline, body)

    if content:
      insert_locale_mapping('content', content, body)
    elif not headline:
      raise ValueError('headline or content must be specified.')

    await self.__request('PATCH', '/projects/@me', body=body)

  async def post_announcement(self, title: str, content: str) -> Announcement:
    """
    Tries to create a new announcement for your project. Announcements appear on your project's page and can be used to notify users about updates, new features, or other news.

    :param title: The announcement's title.
    :type title: :py:class:`str`
    :param content: The announcement's content.
    :type content: :py:class:`str`

    :exception TypeError: The specified title and content is not a :py:class:`str`.
    :exception ValueError: The specified title and content length is not within the accepted ranges.
    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The created announcement.
    :rtype: :class:`.Announcement`
    """

    if not (isinstance(title, str) and isinstance(content, str)):
      raise TypeError('The specified title and content must be a string.')
    elif len(title) < 3 or len(content) < 10:
      raise ValueError(
        'The specified title and content length must be within the accepted ranges.'
      )

    return Announcement(
      await self.__request(
        'POST',
        '/projects/@me/announcements',
        body={'title': title[:100], 'content': content[:2000]},
      )
    )

  async def post_commands(self, commands: list[dict]) -> None:
    """
    Tries to update the application commands list in your Discord bot's Top.gg page.

    :param commands: A list of your Discord bot's application commands in the form of Discord API's raw JSON format.
    :type commands: list[:py:class:`dict`]

    :exception TypeError: The specified commands is not a :py:class:`list` of :py:class:`dict`.
    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.
    """

    if not isinstance(commands, list) or not all(
      isinstance(command, dict) for command in commands
    ):
      raise TypeError(
        "The specified commands is not a list of dicts in the form of Discord API's raw JSON format."
      )

    await self.__request('POST', '/projects/@me/commands', body=commands)

  async def post_metrics(self, metrics: Metrics | dict[datetime, Metrics]) -> None:
    """
    Tries to post a single or batch of metrics payloads for your project. Use this to push fresh numbers after an event such as joining or leaving a guild or a player connecting.

    :param metrics: A single or batch of metrics.
    :type metrics: :class:`.Metrics` | dict[:py:class:`~datetime.datetime`, :class:`.Metrics`]

    :exception TypeError: The specified metrics has an invalid type.
    :exception ValueError: The specified batch of metrics is empty.
    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.
    """

    if not isinstance(metrics, Metrics) and not (
      isinstance(metrics, dict)
      and all(
        isinstance(timestamp, datetime) and isinstance(metrics, Metrics)
        for timestamp, metrics in metrics.items()
      )
    ):
      raise TypeError('The specified metrics has an invalid type.')
    elif not metrics:
      raise ValueError('The specified batch of metrics must not be empty.')
    elif isinstance(metrics, Metrics):
      await self.__request(
        'PATCH',
        '/projects/@me/metrics',
        body=metrics._json,
      )
    else:
      await self.__request(
        'POST',
        '/projects/@me/metrics/batch',
        body=[
          {'timestamp': timestamp.isoformat(), 'metrics': metrics._json}
          for timestamp, metrics in metrics.items()
        ],
      )

  async def get_vote(self, user_source: UserSource, id: int) -> PartialVote | None:
    """
    Tries to get the latest vote information of a user on your project. Returns :py:obj:`None` if the user has not voted.

    :param user_source: The user's source.
    :type user_source: :class:`.UserSource`
    :param id: The user's ID.
    :type id: :py:class:`int`

    :exception TypeError: One or more specified argument types are invalid.
    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The latest vote information of a user on your project or :py:obj:`None` if the user has not voted.
    :rtype: :class:`.PartialVote` | :py:obj:`None`
    """

    if not isinstance(user_source, UserSource) or not isinstance(id, int):
      raise TypeError("The specified user's source and/or ID's type is invalid.")

    try:
      return PartialVote(
        await self.__request(
          'GET', f'/projects/@me/votes/{id}', params={'source': user_source.value}
        )
      )
    except RequestError as err:
      if err.status == 404:
        return

      raise

  async def get_votes(self, since: datetime) -> PaginatedVotes:
    """
    Tries to get a cursor-based paginated list of votes for your project, ordered by creation date.

    :param since: The earliest possible date for all votes.
    :type since: :py:class:`~datetime.datetime`

    :exception TypeError: The specified earliest possible date's type is invalid.
    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: A cursor-based paginated list of votes for your project, ordered by creation date.
    :rtype: :class:`.PaginatedVotes`
    """

    if not isinstance(since, datetime):
      raise TypeError("The specified earliest possible date's type is invalid.")

    return await self._get_votes(startDate=since.isoformat())

  async def _get_votes(self, **params: str) -> PaginatedVotes:
    return PaginatedVotes(
      self, await self.__request('GET', '/projects/@me/votes', params=params)
    )

  async def close(self) -> None:
    """Closes the :class:`.Client` object. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    if self.__own_session and not self.__session.closed:
      await self.__session.close()

  async def __aenter__(self) -> 'Client':
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()

