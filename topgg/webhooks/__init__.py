# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from .models import (
  IntegrationCreate,
  IntegrationDelete,
  Project,
  Test,
  User,
  VoteCreate,
)
from .helpers import parse, verify
from .. import VERSION


__title__ = 'topggpy'
__author__ = 'null8626 & Top.gg'
__credits__ = ('null8626', 'Top.gg')
__maintainer__ = 'null8626'
__status__ = 'Production'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2024-2026 null8626 & Top.gg'
__version__ = VERSION
__all__ = (
  'IntegrationCreate',
  'IntegrationDelete',
  'parse',
  'Project',
  'Test',
  'User',
  'verify',
  'VoteCreate',
)
