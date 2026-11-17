# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg


class Error(Exception):
  """The base error class. Extends :py:class:`Exception`."""

  __slots__: tuple[str, ...] = ()


class RequestError(Error):
  """Thrown upon HTTP request failure. Extends :class:`.Error`."""

  __slots__: tuple[str, ...] = ('data', 'status')

  data: dict | None
  """The JSON error data returned from the API."""

  status: int | None
  """The status code returned from the API."""

  def __init__(self, data: dict | None, status: int | None):
    self.data = data
    self.status = status

    super().__init__(f'Got {status}: {data!r}')

  def __repr__(self) -> str:
    return f'<{__class__.__name__} type={self.type!r} title={self.title!r} status={self.status} detail={self.detail!r} code={self.code!r} data={self.data!r}>'

  @property
  def type(self) -> str | None:
    """The URI identifying the error type."""

    if self.data is not None:
      return self.data.get('type')

  @property
  def title(self) -> str | None:
    """The error's short human-readable summary."""

    if self.data is not None:
      return self.data.get('title')

  @property
  def detail(self) -> str | None:
    """The human-readable explanation of this specific occurrence."""

    if self.data is not None:
      return self.data.get('detail')

  @property
  def code(self) -> str | None:
    """The error's code (e.g. ``PROJECT_NOT_FOUND``.)"""

    if self.data is not None:
      return self.data.get('code')


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
