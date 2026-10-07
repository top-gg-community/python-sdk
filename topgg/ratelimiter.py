# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from collections import deque
from time import time
import asyncio

if TYPE_CHECKING:
  from types import TracebackType


MAXIMUM_DELAY_THRESHOLD = 5 * 60


@dataclass(repr=False, slots=True)
class Ratelimiter:
  """Handles ratelimits for a specific endpoint."""

  _max_calls: int
  _period: float = 1.0
  _calls: deque[float] = field(default_factory=deque)
  _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
  _cancelled_delay: bool = field(default=False, init=False)

  async def __aenter__(self) -> 'Ratelimiter':
    """Delays the request to this endpoint if it could lead to a ratelimit."""

    async with self._lock:
      if len(self._calls) >= self._max_calls:
        now = time()
        until = now + self._period - self._timespan

        if (sleep_time := until - now) > 0:
          if sleep_time <= (MAXIMUM_DELAY_THRESHOLD):
            await asyncio.sleep(sleep_time)
          else:
            self._cancelled_delay = True

      return self

  async def __aexit__(
    self,
    _exc_type: type[BaseException],
    _exc_val: BaseException,
    _exc_tb: 'TracebackType',
  ) -> None:
    """Stores the previous request's timestamp."""

    async with self._lock:
      if self._cancelled_delay:
        self._cancelled_delay = False
      else:
        self._calls.append(time())

        while self._timespan >= self._period:
          self._calls.popleft()

  @property
  def _timespan(self) -> float:
    """The timespan between the first call and last call."""

    if len(self._calls) < 2:
      return 0.0
    return self._calls[-1] - self._calls[0]
