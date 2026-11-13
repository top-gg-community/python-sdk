# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from . import webhooks
from .client import (
  Client,
  Oauth2,
  Oauth2Client,
  Oauth2Session,
  Oauth2SessionGuard,
  Oauth2URL,
)
from .errors import Error, Ratelimited, RequestError
from .models import (
  AnnouncementCategory,
  BaseWebhook,
  DiscordBotMetrics,
  DiscordServerMetrics,
  Integration,
  Locale,
  LocaleMap,
  Metrics,
  Paginated,
  PartialProject,
  PartialVote,
  Platform,
  Project,
  ProjectSubmission,
  ProjectType,
  ReviewStatus,
  RobloxGameMetrics,
  TimestampedMetrics,
  User,
  UserConnection,
  UserProject,
  UserSource,
  Vote,
  Webhook,
)
from .version import VERSION

__title__ = 'topggpy'
__author__ = 'null8626 & Top.gg'
__credits__ = ('null8626', 'Top.gg')
__maintainer__ = 'null8626'
__status__ = 'Production'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2024-2026 null8626 & Top.gg'
__version__ = VERSION
__all__ = (
  'VERSION',
  'AnnouncementCategory',
  'BaseWebhook',
  'Client',
  'DiscordBotMetrics',
  'DiscordServerMetrics',
  'Error',
  'Integration',
  'Locale',
  'LocaleMap',
  'Metrics',
  'Oauth2',
  'Oauth2Client',
  'Oauth2Session',
  'Oauth2SessionGuard',
  'Oauth2URL',
  'Paginated',
  'PartialProject',
  'PartialVote',
  'Platform',
  'Project',
  'ProjectSubmission',
  'ProjectType',
  'Ratelimited',
  'RequestError',
  'ReviewStatus',
  'RobloxGameMetrics',
  'TimestampedMetrics',
  'User',
  'UserConnection',
  'UserProject',
  'UserSource',
  'Vote',
  'Webhook',
  'webhooks',
)
