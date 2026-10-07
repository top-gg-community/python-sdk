# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 null8626 & Top.gg

from typing import TYPE_CHECKING

from .client import BASE_URL
from .project import Platform, ProjectType


class Widget:
  """A Top.gg widget URL generator."""

  __slots__: tuple[str, ...] = ()

  @staticmethod
  def large(platform: 'Platform', project_type: ProjectType, id: int) -> str:
    """
    Generates a large widget URL.

    :param platform: The project's platform.
    :type platform: :class:`.Platform`
    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's ID.
    :type id: :py:class:`int`

    :exception TypeError: The specified platform, project type, and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(platform, Platform) or not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError(
        "The specified platform, project type, and/or project ID's type is invalid."
      )

    return f'{BASE_URL}/widgets/large/{platform.value}/{project_type.value}/{id}'

  @staticmethod
  def votes(platform: Platform, project_type: ProjectType, id: int) -> str:
    """
    Generates a small widget URL for displaying votes.

    :param platform: The project's platform.
    :type platform: :class:`.Platform`
    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's ID.
    :type id: :py:class:`int`

    :exception TypeError: The specified platform, project type, and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(platform, Platform) or not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError(
        "The specified platform, project type, and/or project ID's type is invalid."
      )

    return f'{BASE_URL}/widgets/small/votes/{platform.value}/{project_type.value}/{id}'

  @staticmethod
  def owner(platform: Platform, project_type: ProjectType, id: int) -> str:
    """
    Generates a small widget URL for displaying a project's owner.

    :param platform: The project's platform.
    :type platform: :class:`.Platform`
    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's ID.
    :type id: :py:class:`int`

    :exception TypeError: The specified platform, project type, and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(platform, Platform) or not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError(
        "The specified platform, project type, and/or project ID's type is invalid."
      )

    return f'{BASE_URL}/widgets/small/owner/{platform.value}/{project_type.value}/{id}'

  @staticmethod
  def social(platform: Platform, project_type: ProjectType, id: int) -> str:
    """
    Generates a small widget URL for displaying social stats.

    :param platform: The project's platform.
    :type platform: :class:`.Platform`
    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's ID.
    :type id: :py:class:`int`

    :exception TypeError: The specified platform, project type, and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(platform, Platform) or not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError(
        "The specified platform, project type, and/or project ID's type is invalid."
      )

    return f'{BASE_URL}/widgets/small/social/{platform.value}/{project_type.value}/{id}'
