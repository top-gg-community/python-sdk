# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg


class Error(Exception):
  """The base error class. Extends :py:class:`Exception`."""

  __slots__: tuple[str, ...] = ()


class RequestError(Error):
  """Thrown upon HTTP request failure. Extends :class:`.Error`."""

  __slots__: tuple[str, ...] = ('code', 'detail', 'status', 'title', 'type')

  type: str | None
  """The URI identifying the error type."""

  title: str | None
  """The error's short human-readable summary."""

  status: int | None
  """The error's HTTP status code."""

  detail: str | None
  """The human-readable explanation of this specific occurrence."""

  code: str | None
  """The error's code (e.g. ``PROJECT_NOT_FOUND``.)"""

  def __init__(self, data: dict | None, status: int | None):
    data = data or {}

    self.type = data.get('type')
    self.title = data.get('title')
    self.status = status or data.get('status')
    self.detail = data.get('detail')
    self.code = data.get('code', data.get('error'))

    super().__init__(f'Got {status}: {data!r}')

  def __repr__(self) -> str:
    return f'<{__class__.__name__} type={self.type!r} title={self.title!r} status={self.status} detail={self.detail!r} code={self.code!r}>'


class Ratelimited(Error):
  """Thrown upon HTTP request failure due to the client being ratelimited. Because of this, the client is not allowed to make requests for a period of time. Extends :class:`.Error`."""

  __slots__: tuple[str, ...] = ('retry_after',)

  retry_after: int
  """How long the client should wait (in seconds) until it can make a request to the API again."""

  def __init__(self, retry_after: int):
    self.retry_after = retry_after

    super().__init__(
      f'The client is blocked by the API. Please try again in {retry_after} seconds.'
    )

  def __repr__(self) -> str:
    return f'<{__class__.__name__} retry_after={self.retry_after}>'
