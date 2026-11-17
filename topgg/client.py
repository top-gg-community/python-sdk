# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

import base64
import hashlib
import json
import secrets
from abc import ABC, abstractmethod
from asyncio import Lock, Task, create_task, sleep
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Self
from urllib.parse import quote_plus

from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from yarl import Query

from .errors import Error, Ratelimited, RequestError
from .models import (
  AnnouncementCategory,
  BaseWebhook,
  Integration,
  LocaleMap,
  Metrics,
  Paginated,
  PartialProject,
  PartialVote,
  Project,
  ProjectSubmission,
  TimestampedMetrics,
  User,
  UserProject,
  UserSource,
  Vote,
  Webhook,
)
from .version import VERSION

API_VERSION = 'v1'
BASE_URL = f'https://top.gg/api/{API_VERSION}'
MAXIMUM_DELAY_THRESHOLD = 5.0


class HttpClient:
  """An HTTP client."""

  __slots__: tuple[str, ...] = ('_own_session', '_session')

  _own_session: bool
  _session: ClientSession

  def __init__(self, session: ClientSession | None = None):
    self._own_session = session is None
    self._session = session or ClientSession(timeout=ClientTimeout(total=5.0))

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self._session!r}>'

  def _get_token(self) -> str | None:  # pragma: nocover
    pass

  async def _ensure_session(self) -> None:  # pragma: nocover
    pass

  async def _request(
    self,
    method: str,
    path: str,
    headers: dict[str, Any],
    *,
    params: Query = None,
    body: Any = None,
    with_token: bool = True,
  ) -> Any:
    if self._session.closed:
      raise Error('Client session is already closed.')

    await self._ensure_session()

    if with_token:
      headers['Authorization'] = f'Bearer {self._get_token()}'

    headers['User-Agent'] = (
      f'topggpy (https://github.com/top-gg-community/python-sdk {VERSION}) Python/'
    )

    kwargs = {}

    if params is not None:
      kwargs['params'] = params

    if body is not None:
      kwargs['data'] = body if isinstance(body, str) else json.dumps(body)

    status = None
    retry_after = 0
    output = None

    try:
      async with self._session.request(
        method, BASE_URL + path, headers=headers, **kwargs
      ) as resp:
        status = resp.status

        try:
          retry_after = int(resp.headers.get('retry-after', 0))
          output = await resp.json()
        except (
          ClientResponseError,
          ValueError,
          json.decoder.JSONDecodeError,
        ):  # pragma: nocover
          pass

        resp.raise_for_status()

        return output
    except ClientResponseError:
      if status == 429 and retry_after is not None:
        if retry_after > MAXIMUM_DELAY_THRESHOLD:
          raise Ratelimited(retry_after) from None
        else:  # pragma: nocover
          await sleep(retry_after)

          return await self._request(
            method, path, headers, params=params, body=body, with_token=with_token
          )

      raise RequestError(output, status) from None

  async def close(self) -> None:
    """Closes the :class:`.HttpClient` object. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    if self._own_session and not self._session.closed:
      await self._session.close()


class ProjectClient(HttpClient):
  """
  An API client using a project token.

  :param token: The project token to use.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None`  (creates a new one instead).
  :type session: :class:`~aiohttp.ClientSession` | :py:obj:`None`
  """

  __slots__: tuple[str, ...] = ('_token',)

  _token: str

  def __init__(self, token: str, *, session: ClientSession | None = None):
    super().__init__(session)

    self._token = token

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self._session!r}>'

  def _get_token(self) -> str:
    return self._token

  async def _json_request(
    self,
    method: str,
    path: str,
    *,
    headers: dict[str, Any] = {},
    params: Query = None,
    body: Any = None,
  ) -> Any:
    return await self._request(method, path, headers, params=params, body=body)

  async def get_project(self) -> Project:
    """
    Fetches a project associated with the current token.

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: A project associated with the current token.
    :rtype: :class:`~topgg.models.Project`
    """

    return Project(await self._json_request('GET', '/projects/@me'))

  async def edit_project(self, headline: LocaleMap, page_content: LocaleMap) -> None:
    """
    Updates the headline and/or page content for a project. Both fields are locale-keyed, so you can set content for multiple languages in a single request.

    :param headline: A map of locales to headline strings. Each headline must be between 3 and 140 characters.
    :type headline: :class:`.LocaleMap`
    :param page_content: page_content A map of locales to page content strings (Markdown supported.) Each entry must be between 300 and 50,000 characters.
    :type page_content: :class:`.LocaleMap`

    :exception ValueError: The headline or page_content length does not match the required ranges.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    headline._enforce_constraints(3, 140)
    page_content._enforce_constraints(300, 50000)

    await self._json_request(
      'PATCH',
      '/projects/@me',
      body={'headline': headline._json, 'page_content': page_content._json},
    )

  async def post_announcement(
    self, title: str, content: str, category: AnnouncementCategory
  ) -> None:
    """
    Creates a new announcement for a project. Announcements appear on a project's page and can be used to notify users about updates, new features, or other news.

    :param title: The announcement's title.
    :type title: :py:class:`str`
    :param content: The announcement's body.
    :type content: :py:class:`str`
    :param category: The category to publish the announcement under.
    :type category: :class:`.AnnouncementCategory`

    :exception ValueError: The title or content length does not match the required ranges.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    if not (3 <= len(title) <= 100):
      raise ValueError('Title length is outside of the accepted range.')
    elif not (100 <= len(content) <= 2000):
      raise ValueError('Content length is outside of the accepted range.')

    await self._json_request(
      'POST',
      '/projects/@me/announcements',
      body={'title': title, 'content': content, 'category': category.value},
    )

  async def post_metrics(self, metrics: Metrics) -> None:
    """
    Submits a single metrics payload for a project. Use this to push fresh numbers after an event such as joining or leaving a guild player connecting.

    :param metrics: The metrics payload.
    :type metrics: :class:`.Metrics`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request('PATCH', '/projects/@me/metrics', body=metrics._to_json())

  async def post_timestamped_metrics[M: Metrics](
    self, metrics: TimestampedMetrics[M]
  ) -> None:
    r"""
    Submits up to 100 metrics entries in a single request.

    :param metrics: The metrics payloads.
    :type metrics: :class:`.TimestampedMetrics`\ [:class:`.Metrics`\ ]

    :exception ValueError: The metrics entries length does not match the required range.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    if not (1 <= len(metrics._json) <= 100):
      raise ValueError('Batch length is outside of the accepted range.')

    await self._json_request(
      'POST', '/projects/@me/metrics/batch', body={'data': metrics._json}
    )

  async def post_commands(self, commands: list[dict]) -> None:
    r"""
    Overwrites the list of slash command definitions for a bot project on Top.gg. This is only applicable to bot-type projects on the discord platform.

    :param commands: The array of slash commands in a JSON-stringified Discord API's application command structure format.
    :type commands: :py:class:`list`\ [:py:class:`dict`\ ]

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request('PUT', '/projects/@me/commands', body=commands)

  async def get_votes(
    self, *, since: datetime | None = None, reference: Paginated[Vote] | None = None
  ) -> Paginated[Vote]:
    r"""
    Fetches a cursor-paginated list of votes for a project, ordered by creation date (oldest first within each page.)

    :param since: The creation date frame of reference. Defaults to :py:obj:`None`.
    :type since: :py:class:`~datetime.datetime` | :py:obj:`None`
    :param reference: The previously returned paginated list as a starting reference. Defaults to :py:obj:`None`.
    :type reference: :class:`.Paginated`\ [:class:`.Vote`\ ] | :py:obj:`None`

    :exception ValueError: Missing required arguments or the creation date frame of reference is invalid.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: A cursor-paginated list of votes for a project, ordered by creation date (oldest first within each page.)
    :rtype: :class:`.Paginated`\ [:class:`.Vote`\ ]
    """

    if getattr(reference, 'is_last', False):
      raise Error('The reference is already on the last page.')

    params = {}

    if since is not None:
      now_timestamp = datetime.now(UTC).timestamp()
      since_timestamp = since.timestamp()

      if now_timestamp < since_timestamp or (
        (now_timestamp - since_timestamp) > 31536000
      ):
        raise ValueError('Invalid since timestamp.')

      params['startDate'] = since.isoformat()
    elif reference is not None:
      params['cursor'] = reference._cursor
    else:
      raise ValueError('Missing required arguments.')

    return Paginated(
      Vote,
      'data',
      await self._json_request('GET', '/projects/@me/votes', params=params),
    )

  async def get_vote(
    self, user_id: int, source: UserSource
  ) -> PartialVote | None:
    """
    Fetches the most recent vote for a specific user.

    :param user_id: The ID of the user to look up. The expected format depends on the source parameter.
    :type user_id: :py:class:`int`
    :param source: The ID type being provided.
    :type source: :class:`.UserSource`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The most recent vote for a specific user if it exists.
    :rtype: :class:`.PartialVote` | :py:obj:`None`
    """

    try:
      return PartialVote(
        await self._json_request(
          'GET', f'/projects/@me/votes/{user_id}', params={'source': source.value}
        )
      )
    except RequestError as error:
      if error.status != 404 or error.code != 'VOTE_EXPIRED':  # pragma: nocover
        raise

  async def __aenter__(self) -> Self:
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()


class ApplicationClient(HttpClient):
  """
  An API client using an application token.

  :param token: The application token to use.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None` (creates a new one instead).
  :type session: :class:`~aiohttp.ClientSession` | :py:obj:`None`
  """

  __slots__: tuple[str, ...] = ('_token',)

  _token: str

  def __init__(self, token: str, *, session: ClientSession | None = None):
    super().__init__(session)

    self._token = token

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self._session!r}>'

  def _get_token(self) -> str:
    return self._token

  async def _json_request(
    self,
    method: str,
    path: str,
    *,
    headers: dict[str, Any] = {},
    params: Query = None,
    body: Any = None,
  ) -> Any:
    return await self._request(method, path, headers, params=params, body=body)

  async def get_projects(
    self, reference: Paginated[PartialProject] | None = None
  ) -> Paginated[PartialProject]:
    r"""
    Fetches the projects the current credential covers.

    :param reference: The previously returned paginated list as a starting reference. Defaults to :py:obj:`None`.
    :type reference: :class:`.Paginated`\ [:class:`.PartialProject`\ ] | :py:obj:`None`

    :exception Error: The reference is already on the last page or the client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The projects the current credential covers.
    :rtype: :class:`.Paginated`\ [:class:`.PartialProject`\ ]
    """

    if getattr(reference, 'is_last', False):
      raise Error('The reference is already on the last page.')

    params = {}

    if cursor := getattr(reference, '_cursor', None):  # pragma: nocover
      params['cursor'] = cursor

    return Paginated(
      PartialProject,
      'projects',
      await self._json_request('GET', '/projects', params=params),
    )

  async def get_project(self, id: int) -> Project:
    """
    Fetches a project associated with the current token.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: A project associated with the current token.
    :rtype: :class:`~.models.Project`
    """

    return Project(await self._json_request('GET', f'/projects/{id}'))

  async def edit_project(
    self, id: int, headline: LocaleMap, page_content: LocaleMap
  ) -> None:
    """
    Updates the headline and/or page content for a project. Both fields are locale-keyed, so you can set content for multiple languages in a single request.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param headline: A map of locales to headline strings. Each headline must be between 3 and 140 characters.
    :type headline: :class:`.LocaleMap`
    :param page_content: page_content A map of locales to page content strings (Markdown supported.) Each entry must be between 300 and 50,000 characters.
    :type page_content: :class:`.LocaleMap`

    :exception ValueError: The headline or page_content length does not match the required ranges.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    headline._enforce_constraints(3, 140)
    page_content._enforce_constraints(300, 50000)

    await self._json_request(
      'PATCH',
      f'/projects/{id}',
      body={'headline': headline._json, 'page_content': page_content._json},
    )

  async def post_announcement(
    self, id: int, title: str, content: str, category: AnnouncementCategory
  ) -> None:
    """
    Creates a new announcement for a project. Announcements appear on a project's page and can be used to notify users about updates, new features, or other news.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param title: The announcement's title.
    :type title: :py:class:`str`
    :param content: The announcement's body.
    :type content: :py:class:`str`
    :param category: The category to publish the announcement under.
    :type category: :class:`.AnnouncementCategory`

    :exception ValueError: The title or content length does not match the required ranges.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    if not (3 <= len(title) <= 100):
      raise ValueError('Title length is outside of the accepted range.')
    elif not (100 <= len(content) <= 2000):
      raise ValueError('Content length is outside of the accepted range.')

    await self._json_request(
      'POST',
      f'/projects/{id}/announcements',
      body={'title': title, 'content': content, 'category': category.value},
    )

  async def post_metrics(self, id: int, metrics: Metrics) -> None:
    """
    Submits a single metrics payload for a project. Use this to push fresh numbers after an event such as joining or leaving a guild player connecting.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param metrics: The metrics payload.
    :type metrics: :class:`.Metrics`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request(
      'PATCH', f'/projects/{id}/metrics', body=metrics._to_json()
    )

  async def post_timestamped_metrics[M: Metrics](
    self, id: int, metrics: TimestampedMetrics[M]
  ) -> None:
    r"""
    Submits up to 100 metrics entries in a single request.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param metrics: The metrics payloads.
    :type metrics: :class:`.TimestampedMetrics`\ [:class:`.Metrics`\ ]

    :exception ValueError: The metrics entries length does not match the required range.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    if not (1 <= len(metrics._json) <= 100):
      raise ValueError('Batch length is outside of the accepted range.')

    await self._json_request(
      'POST', f'/projects/{id}/metrics/batch', body={'data': metrics._json}
    )

  async def post_commands(self, id: int, commands: list[dict]) -> None:
    r"""
    Overwrites the list of slash command definitions for a bot project on Top.gg. This is only applicable to bot-type projects on the discord platform.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param commands: The array of slash commands in a JSON-stringified Discord API's application command structure format.
    :type commands: :py:class:`list`\ [:py:class:`dict`\ ]

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request('PUT', f'/projects/{id}/commands', body=commands)

  async def get_votes(
    self,
    id: int,
    *,
    since: datetime | None = None,
    reference: Paginated[Vote] | None = None,
  ) -> Paginated[Vote]:
    r"""
    Fetches a cursor-paginated list of votes for a project, ordered by creation date (oldest first within each page.)

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param since: The creation date frame of reference. Defaults to :py:obj:`None`.
    :type since: :py:class:`~datetime.datetime` | :py:obj:`None`
    :param reference: The previously returned paginated list as a starting reference. Defaults to :py:obj:`None`.
    :type reference: :class:`.Paginated`\ [:class:`.Vote`\ ] | :py:obj:`None`

    :exception ValueError: Missing required arguments or the creation date frame of reference is invalid.
    :exception Error: The reference is already on the last page or the client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: A cursor-paginated list of votes for a project, ordered by creation date (oldest first within each page.)
    :rtype: :class:`.Paginated`\ [:class:`.Vote`\ ]
    """

    if getattr(reference, 'is_last', False):
      raise Error('The reference is already on the last page.')

    params = {}

    if since is not None:
      now_timestamp = datetime.now(UTC).timestamp()
      since_timestamp = since.timestamp()

      if now_timestamp < since_timestamp or (
        (now_timestamp - since_timestamp) > 31536000
      ):
        raise ValueError('Invalid since timestamp.')

      params['startDate'] = since.isoformat()
    elif reference is not None:
      params['cursor'] = reference._cursor
    else:
      raise ValueError('Missing required arguments.')

    return Paginated(
      Vote,
      'data',
      await self._json_request('GET', f'/projects/{id}/votes', params=params),
    )

  async def get_vote(
    self, id: int, user_id: int, source: UserSource
  ) -> PartialVote | None:
    """
    Fetches the most recent vote for a specific user.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param user_id: The ID of the user to look up. The expected format depends on the source parameter.
    :type user_id: :py:class:`int`
    :param source: The ID type being provided.
    :type source: :class:`.UserSource`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The most recent vote for a specific user if it exists.
    :rtype: :class:`.PartialVote` | :py:obj:`None`
    """

    try:
      return PartialVote(
        await self._json_request(
          'GET', f'/projects/{id}/votes/{user_id}', params={'source': source.value}
        )
      )
    except RequestError as error:
      if error.status != 404 or error.code != 'VOTE_EXPIRED':  # pragma: nocover
        raise

  async def get_integrations(self, id: int) -> list[Integration]:
    r"""
    Fetches the integrations available for a project and whether each one is connected.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The integrations available for a project and whether each one is connected.
    :rtype: :py:class:`list`\ [:class:`.Integration`\ ]
    """

    return [
      Integration(integration)
      for integration in await self._json_request('GET', f'/projects/{id}/integrations')
    ]

  async def connect_integration(
    self, project_id: int, integration_id: int
  ) -> None:
    """
    Connects an integration to the project. Top.gg runs the integration handshake and starts delivering events to it.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param integration_id: The integration's Top.gg ID.
    :type integration_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request(
      'PUT', f'/projects/{project_id}/integrations/{integration_id}'
    )

  async def disconnect_integration(
    self, project_id: int, integration_id: int
  ) -> None:
    """
    Disconnects an integration the application connected. The integration receives an integration.delete event.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param integration_id: The integration's Top.gg ID.
    :type integration_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request(
      'DELETE', f'/projects/{project_id}/integrations/{integration_id}'
    )

  async def get_webhooks(self, id: int) -> list[Webhook]:
    r"""
    Fetches the webhooks the application created on the project.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The webhooks the application created on the project.
    :rtype: :py:class:`list`\ [:class:`.Webhook`\ ]
    """

    return [
      Webhook(webhook)
      for webhook in await self._json_request('GET', f'/projects/{id}/webhooks')
    ]

  async def create_webhook(self, id: int, webhook: BaseWebhook) -> Webhook:
    """
    Creates a vote webhook on the project.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param webhook: The vote webhook.
    :type webhook: :class:`.BaseWebhook`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The created webhook.
    :rtype: :class:`.Webhook`
    """

    return Webhook(
      await self._json_request(
        'POST',
        f'/projects/{id}/webhooks',
        body={'label': webhook.label, 'url': webhook.url},
      )
    )

  async def delete_webhook(self, project_id: int, webhook_id: int) -> None:
    """
    Deletes a webhook the application created.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param webhook_id: The webhook's Top.gg ID.
    :type webhook_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request('DELETE', f'/projects/{project_id}/webhooks/{webhook_id}')

  async def rotate_webhook_secret(
    self, project_id: int, webhook_id: int
  ) -> str:
    """
    Replaces the signing secret of a webhook the application created. The previous secret stops working immediately.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param webhook_id: The webhook's Top.gg ID.
    :type webhook_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The new webhook secret.
    :rtype: :py:class:`str`
    """

    return (
      await self._json_request(
        'POST', f'/projects/{project_id}/webhooks/{webhook_id}/rotate'
      )
    )['secret']

  async def test_webhook(self, project_id: int, webhook_id: int) -> None:
    """
    Sends a webhook.test event to a webhook the application created.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param webhook_id: The webhook's Top.gg ID.
    :type webhook_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request(
      'POST', f'/projects/{project_id}/webhooks/{webhook_id}/test'
    )

  async def __aenter__(self) -> Self:
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()


class Oauth2Session:
  """
  An oauth2 session.

  :param token: The session's access token. Defaults to :py:obj:`None`.
  :type token: :py:class:`str` | :py:obj:`None`
  :param refresh_token: The session's refresh token. Defaults to :py:obj:`None`.
  :type refresh_token: :py:class:`str` | :py:obj:`None`
  :param expires_at: When the session's access token expires. Defaults to :py:obj:`None`.
  :type expires_at: :py:class:`~datetime.datetime` | :py:obj:`None`
  :param json: The API's raw JSON format.
  :type json: :py:class:`dict`
  """

  __slots__: tuple[str, ...] = ('token', 'refresh_token', 'expires_at')

  token: str
  """The session's access token."""

  refresh_token: str
  """The session's refresh token."""

  expires_at: datetime
  """When the session's access token expires."""

  def __init__(
    self,
    *,
    token: str | None = None,
    refresh_token: str | None = None,
    expires_at: datetime | None = None,
    json: dict = {},
  ):
    self.token = token or json['access_token']
    self.refresh_token = refresh_token or json['refresh_token']
    self.expires_at = expires_at or datetime.now(UTC) + timedelta(
      seconds=json['expires_in']
    )

  def __repr__(self) -> str:
    return f'<{__class__.__name__} expires_at={self.expires_at!r}>'

  @property
  def has_expired(self) -> bool:
    """Whether the session's access token has expired."""

    return datetime.now(UTC) >= self.expires_at


@dataclass(frozen=True, repr=False, slots=True)
class Oauth2URL:
  """An oauth2 URL."""

  _oauth2: 'Oauth2'

  state: str
  """The state."""

  code_verifier: str
  """The code verifier."""

  url: str
  """The URL."""

  def __repr__(self) -> str:
    return f'<{__class__.__name__} state={self.state!r} code_verifier={self.code_verifier!r} url={self.url!r}>'

  def __str__(self) -> str:
    return self.url

  async def exchange(self, code: str) -> Oauth2Session:
    """
    Exchanges an authorization code for an oauth2 session.

    :param code: The request's code query parameter.
    :type code: :py:class:`str`

    :returns: The new oauth2 session.
    :rtype: :class:`.Oauth2Session`
    """

    body = f'grant_type=authorization_code&client_id={self._oauth2._client_id}&client_secret={self._oauth2._client_secret}&code={quote_plus(code)}&redirect_uri={quote_plus(self._oauth2._redirect_uri)}&code_verifier={quote_plus(self.code_verifier)}'

    data = await self._oauth2._http._request(
      'POST',
      '/oauth2/token',
      {'Content-Type': 'application/x-www-form-urlencoded'},
      body=body,
    )

    return Oauth2Session(json=data)


class Oauth2:
  """An oauth2 manager."""

  __slots__: tuple[str, ...] = (
    '_client_id',
    '_client_secret',
    '_http',
    '_redirect_uri',
    '_scope',
  )

  _client_id: int
  _client_secret: str
  _redirect_uri: str
  _scope: str
  _http: HttpClient

  def __init__(
    self,
    client_id: int,
    client_secret: str,
    redirect_uri: str,
    scopes: list[str],
    *,
    session: ClientSession | None = None,
  ):
    self._client_id = client_id
    self._client_secret = client_secret
    self._redirect_uri = redirect_uri
    self._scope = '+'.join(scopes)
    self._http = HttpClient(session)

  def __repr__(self) -> str:
    return f'<{__class__.__name__} client_id={self._client_id!r} redirect_uri={self._redirect_uri!r} scope={self._scope!r}>'

  def new_client(self, session: Oauth2Session) -> 'Oauth2Client':
    """
    Creates an oauth2 API client from an oauth2 session.

    :param session: The session.
    :type session: :class:`.Oauth2Session`

    :returns: The new oauth2 API client.
    :rtype: :class:`.Oauth2Client`
    """

    return Oauth2Client(self, session)

  def new_url(
    self, state: str | None = None, code_verifier: str | None = None
  ) -> Oauth2URL:
    """
    Creates an oauth2 URL.

    :param state: The existing state. Defaults to :py:obj:`None`.
    :type state: :py:class:`str` | :py:obj:`None`.
    :param code_verifier: The existing code verifier. Defaults to :py:obj:`None`.
    :type code_verifier: :py:class:`str` | :py:obj:`None`.

    :returns: The new oauth2 URL.
    :rtype: :class:`.Oauth2URL`
    """

    state = state or secrets.token_hex(64)
    code_verifier = code_verifier or secrets.token_hex(64)
    code_challenge = (
      base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('ascii')).digest())
      .decode('ascii')
      .rstrip('=')
    )

    return Oauth2URL(
      self,
      state,
      code_verifier,
      f'https://top.gg/oauth2/authorize?response_type=code&code_challenge_method=S256&client_id={self._client_id}&redirect_uri={quote_plus(self._redirect_uri)}&state={quote_plus(state)}&code_challenge={quote_plus(code_challenge)}&scope={self._scope}',
    )

  async def close(self) -> None:
    """Closes the :class:`.Oauth2` object. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    await self._http.close()


class Oauth2Client(HttpClient):
  """An oauth2 API client."""

  __slots__: tuple[str, ...] = (
    '_oauth2',
    '_oauth2_session',
  )

  _oauth2: Oauth2
  _oauth2_session: Oauth2Session

  def __init__(self, oauth2: Oauth2, session: Oauth2Session):
    super().__init__(session=oauth2._http._session)

    self._oauth2 = oauth2
    self._oauth2_session = session

  def __repr__(self) -> str:
    return f'<{__class__.__name__} oauth2={self._oauth2!r} oauth2_session={self._oauth2_session!r}>'

  def _get_token(self) -> str:
    return self._oauth2_session.token

  async def _ensure_session(self) -> None:
    if not self._oauth2_session.has_expired:
      return

    body = f'grant_type=refresh_token&client_id={self._oauth2._client_id}&client_secret={self._oauth2._client_secret}&refresh_token={self._oauth2_session.refresh_token}'

    data = await self._oauth2._http._request(
      'POST',
      '/oauth2/token',
      {'Content-Type': 'application/x-www-form-urlencoded'},
      body=body,
    )

    self._oauth2_session = Oauth2Session(json=data)

  async def _json_request(
    self,
    method: str,
    path: str,
    *,
    headers: dict[str, Any] = {},
    params: Query = None,
    body: Any = None,
  ) -> Any:
    return await self._request(method, path, headers, params=params, body=body)

  @property
  def has_expired(self) -> bool:
    """Whether the client's session access token has expired."""

    return self._oauth2_session.has_expired

  async def get_projects(
    self, reference: Paginated[PartialProject] | None = None
  ) -> Paginated[PartialProject]:
    r"""
    Fetches the projects the current credential covers.

    :param reference: The previously returned paginated list as a starting reference. Defaults to :py:obj:`None`.
    :type reference: :class:`.Paginated`\ [:class:`.PartialProject`\ ] | :py:obj:`None`

    :exception Error: The reference is already on the last page or the client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The projects the current credential covers.
    :rtype: :class:`.Paginated`\ [:class:`.PartialProject`\ ]
    """

    if getattr(reference, 'is_last', False):
      raise Error('The reference is already on the last page.')

    params = {}

    if cursor := getattr(reference, '_cursor', None):  # pragma: nocover
      params['cursor'] = cursor

    return Paginated(
      PartialProject,
      'projects',
      await self._json_request('GET', '/projects', params=params),
    )

  async def get_project(self, id: int) -> Project:
    """
    Fetches a project associated with the current token.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: A project associated with the current token.
    :rtype: :class:`~.models.Project`
    """

    return Project(await self._json_request('GET', f'/projects/{id}'))

  async def edit_project(
    self, id: int, headline: LocaleMap, page_content: LocaleMap
  ) -> None:
    """
    Updates the headline and/or page content for a project. Both fields are locale-keyed, so you can set content for multiple languages in a single request.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param headline: A map of locales to headline strings. Each headline must be between 3 and 140 characters.
    :type headline: :class:`.LocaleMap`
    :param page_content: page_content A map of locales to page content strings (Markdown supported.) Each entry must be between 300 and 50,000 characters.
    :type page_content: :class:`.LocaleMap`

    :exception ValueError: The headline or page_content length does not match the required ranges.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    headline._enforce_constraints(3, 140)
    page_content._enforce_constraints(300, 50000)

    await self._json_request(
      'PATCH',
      f'/projects/{id}',
      body={'headline': headline._json, 'page_content': page_content._json},
    )

  async def post_announcement(
    self, id: int, title: str, content: str, category: AnnouncementCategory
  ) -> None:
    """
    Creates a new announcement for a project. Announcements appear on a project's page and can be used to notify users about updates, new features, or other news.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param title: The announcement's title.
    :type title: :py:class:`str`
    :param content: The announcement's body.
    :type content: :py:class:`str`
    :param category: The category to publish the announcement under.
    :type category: :class:`.AnnouncementCategory`

    :exception ValueError: The title or content length does not match the required ranges.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    if not (3 <= len(title) <= 100):
      raise ValueError('Title length is outside of the accepted range.')
    elif not (100 <= len(content) <= 2000):
      raise ValueError('Content length is outside of the accepted range.')

    await self._json_request(
      'POST',
      f'/projects/{id}/announcements',
      body={'title': title, 'content': content, 'category': category.value},
    )

  async def post_metrics(self, id: int, metrics: Metrics) -> None:
    """
    Submits a single metrics payload for a project. Use this to push fresh numbers after an event such as joining or leaving a guild player connecting.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param metrics: The metrics payload.
    :type metrics: :class:`.Metrics`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request(
      'PATCH', f'/projects/{id}/metrics', body=metrics._to_json()
    )

  async def post_timestamped_metrics[M: Metrics](
    self, id: int, metrics: TimestampedMetrics[M]
  ) -> None:
    r"""
    Submits up to 100 metrics entries in a single request.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param metrics: The metrics payloads.
    :type metrics: :class:`.TimestampedMetrics`\ [:class:`.Metrics`\ ]

    :exception ValueError: The metrics entries length does not match the required range.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    if not (1 <= len(metrics._json) <= 100):
      raise ValueError('Batch length is outside of the accepted range.')

    await self._json_request(
      'POST', f'/projects/{id}/metrics/batch', body={'data': metrics._json}
    )

  async def post_commands(self, id: int, commands: list[dict]) -> None:
    r"""
    Overwrites the list of slash command definitions for a bot project on Top.gg. This is only applicable to bot-type projects on the discord platform.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param commands: The array of slash commands in a JSON-stringified Discord API's application command structure format.
    :type commands: :py:class:`list`\ [:py:class:`dict`\ ]

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request('PUT', f'/projects/{id}/commands', body=commands)

  async def get_votes(
    self,
    id: int,
    *,
    since: datetime | None = None,
    reference: Paginated[Vote] | None = None,
  ) -> Paginated[Vote]:
    r"""
    Fetches a cursor-paginated list of votes for a project, ordered by creation date (oldest first within each page.)

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param since: The creation date frame of reference. Defaults to :py:obj:`None`.
    :type since: :py:class:`~datetime.datetime` | :py:obj:`None`
    :param reference: The previously returned paginated list as a starting reference. Defaults to :py:obj:`None`.
    :type reference: :class:`.Paginated`\ [:class:`.Vote`\ ] | :py:obj:`None`

    :exception ValueError: Missing required arguments or the creation date frame of reference is invalid.
    :exception Error: The reference is already on the last page or the client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: A cursor-paginated list of votes for a project, ordered by creation date (oldest first within each page.)
    :rtype: :class:`.Paginated`\ [:class:`.Vote`\ ]
    """

    if getattr(reference, 'is_last', False):
      raise Error('The reference is already on the last page.')

    params = {}

    if since is not None:
      now_timestamp = datetime.now(UTC).timestamp()
      since_timestamp = since.timestamp()

      if now_timestamp < since_timestamp or (
        (now_timestamp - since_timestamp) > 31536000
      ):
        raise ValueError('Invalid since timestamp.')

      params['startDate'] = since.isoformat()
    elif reference is not None:
      params['cursor'] = reference._cursor
    else:
      raise ValueError('Missing required arguments.')

    return Paginated(
      Vote,
      'data',
      await self._json_request('GET', f'/projects/{id}/votes', params=params),
    )

  async def get_vote(
    self, id: int, user_id: int, source: UserSource
  ) -> PartialVote | None:
    """
    Fetches the most recent vote for a specific user.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param user_id: The ID of the user to look up. The expected format depends on the source parameter.
    :type user_id: :py:class:`int`
    :param source: The ID type being provided.
    :type source: :class:`.UserSource`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The most recent vote for a specific user if it exists.
    :rtype: :class:`.PartialVote` | :py:obj:`None`
    """

    try:
      return PartialVote(
        await self._json_request(
          'GET', f'/projects/{id}/votes/{user_id}', params={'source': source.value}
        )
      )
    except RequestError as error:
      if error.status != 404 or error.code != 'VOTE_EXPIRED':  # pragma: nocover
        raise

  async def get_integrations(self, id: int) -> list[Integration]:
    r"""
    Fetches the integrations available for a project and whether each one is connected.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The integrations available for a project and whether each one is connected.
    :rtype: :py:class:`list`\ [:class:`.Integration`\ ]
    """

    return [
      Integration(integration)
      for integration in await self._json_request('GET', f'/projects/{id}/integrations')
    ]

  async def connect_integration(
    self, project_id: int, integration_id: int
  ) -> None:
    """
    Connects an integration to the project. Top.gg runs the integration handshake and starts delivering events to it.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param integration_id: The integration's Top.gg ID.
    :type integration_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request(
      'PUT', f'/projects/{project_id}/integrations/{integration_id}'
    )

  async def disconnect_integration(
    self, project_id: int, integration_id: int
  ) -> None:
    """
    Disconnects an integration the application connected. The integration receives an integration.delete event.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param integration_id: The integration's Top.gg ID.
    :type integration_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request(
      'DELETE', f'/projects/{project_id}/integrations/{integration_id}'
    )

  async def get_webhooks(self, id: int) -> list[Webhook]:
    r"""
    Fetches the webhooks the application created on the project.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The webhooks the application created on the project.
    :rtype: :py:class:`list`\ [:class:`.Webhook`\ ]
    """

    return [
      Webhook(webhook)
      for webhook in await self._json_request('GET', f'/projects/{id}/webhooks')
    ]

  async def create_webhook(self, id: int, webhook: BaseWebhook) -> Webhook:
    """
    Creates a vote webhook on the project.

    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param webhook: The vote webhook.
    :type webhook: :class:`.BaseWebhook`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The created webhook.
    :rtype: :class:`.Webhook`
    """

    return Webhook(
      await self._json_request(
        'POST',
        f'/projects/{id}/webhooks',
        body={'label': webhook.label, 'url': webhook.url},
      )
    )

  async def delete_webhook(self, project_id: int, webhook_id: int) -> None:
    """
    Deletes a webhook the application created.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param webhook_id: The webhook's Top.gg ID.
    :type webhook_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request('DELETE', f'/projects/{project_id}/webhooks/{webhook_id}')

  async def rotate_webhook_secret(
    self, project_id: int, webhook_id: int
  ) -> str:
    """
    Replaces the signing secret of a webhook the application created. The previous secret stops working immediately.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param webhook_id: The webhook's Top.gg ID.
    :type webhook_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The new webhook secret.
    :rtype: :py:class:`str`
    """

    return (
      await self._json_request(
        'POST', f'/projects/{project_id}/webhooks/{webhook_id}/rotate'
      )
    )['secret']

  async def test_webhook(self, project_id: int, webhook_id: int) -> None:
    """
    Sends a webhook.test event to a webhook the application created.

    :param project_id: The project's Top.gg ID.
    :type project_id: :py:class:`int`
    :param webhook_id: The webhook's Top.gg ID.
    :type webhook_id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._json_request(
      'POST', f'/projects/{project_id}/webhooks/{webhook_id}/test'
    )

  async def get_authorized_user(self) -> User:
    """
    Fetches the user who authorized the application.

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The user who authorized the application.
    :rtype: :class:`~topgg.models.User`
    """

    return User(await self._json_request('GET', '/users/@me'))

  async def get_authorized_user_projects(self) -> list[UserProject]:
    r"""
    Fetches the projects owned by the user who authorized the application.

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.

    :returns: The projects owned by the user who authorized the application.
    :rtype: :py:class:`list`\ [:class:`.UserProject`\ ]
    """

    return [
      UserProject(project)
      for project in await self._json_request('GET', '/users/@me/projects')
    ]

  async def submit_project(self, submission: ProjectSubmission) -> None:
    """
    Creates a draft project for the user who authorized the application. Name, icon, and missing descriptions are fetched from the platform. The project starts as a draft; the user completes the listing and submits it for review in their Top.gg dashboard.

    :param submission: The project submission.
    :type submission: :class:`.ProjectSubmission`

    :exception ValueError: The headline or page_content length does not match the required ranges.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    if not (3 <= len(submission.headline) <= 140):
      raise ValueError('Headline length is outside of the accepted range.')
    elif not (300 <= len(submission.page_content) <= 50000):
      raise ValueError('Page content length is outside of the accepted range.')

    await self._json_request(
      'POST',
      '/users/@me/projects',
      body={
        'platform': submission.platform.value,
        'type': submission.type.value,
        'platform_id': str(submission.platform_id),
        'headline': submission.headline,
        'page_content': submission.page_content,
      },
    )

  async def revoke_token(self) -> None:
    """
    Revokes the client's access token.

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: The client is ratelimited from sending more requests.
    """

    await self._oauth2._http._request(
      'POST',
      '/oauth2/revoke',
      {'Content-Type': 'application/x-www-form-urlencoded'},
      body=f'client_id={self._oauth2._client_id}&client_secret={self._oauth2._client_secret}&token={self._oauth2_session.refresh_token}',
    )
