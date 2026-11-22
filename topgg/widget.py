# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from .client import BASE_URL
from .models import Platform, ProjectType


class Widget:
  """A Top.gg widget URL generator."""

  __slots__: tuple[str, ...] = ()

  @staticmethod
  def large(
    platform: Platform, project_type: ProjectType, id: int, *, hide_avatar: bool = False
  ) -> str:
    """
    Generates a large widget URL.

    :param platform: The project's platform.
    :type platform: :class:`.Platform`
    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param hide_avatar: Whether to also hide the project's avatar. Defaults to ``False``.
    :type hide_avatar: :py:class:`bool`

    :exception TypeError: The specified platform, project type, and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError(
        "The specified platform, project type, and/or project ID's type is invalid."
      )

    return f'{BASE_URL}/widgets/large/{platform.value}/{project_type.value}/{id}{"?hideAvatar=true" if hide_avatar else ""}'

  @staticmethod
  def votes(
    platform: Platform, project_type: ProjectType, id: int, *, hide_avatar: bool = False
  ) -> str:
    """
    Generates a small widget URL for displaying votes.

    :param platform: The project's platform.
    :type platform: :class:`.Platform`
    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param hide_avatar: Whether to also hide the project's avatar. Defaults to ``False``.
    :type hide_avatar: :py:class:`bool`

    :exception TypeError: The specified platform, project type, and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError(
        "The specified platform, project type, and/or project ID's type is invalid."
      )

    return f'{BASE_URL}/widgets/small/votes/{platform.value}/{project_type.value}/{id}{"?hideAvatar=true" if hide_avatar else ""}'

  @staticmethod
  def owner(
    platform: Platform, project_type: ProjectType, id: int, *, hide_avatar: bool = False
  ) -> str:
    """
    Generates a small widget URL for displaying a project's owner.

    :param platform: The project's platform.
    :type platform: :class:`.Platform`
    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param hide_avatar: Whether to also hide the project's avatar. Defaults to ``False``.
    :type hide_avatar: :py:class:`bool`

    :exception TypeError: The specified platform, project type, and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError(
        "The specified platform, project type, and/or project ID's type is invalid."
      )

    return f'{BASE_URL}/widgets/small/owner/{platform.value}/{project_type.value}/{id}{"?hideAvatar=true" if hide_avatar else ""}'

  @staticmethod
  def social(
    platform: Platform, project_type: ProjectType, id: int, *, hide_avatar: bool = False
  ) -> str:
    """
    Generates a small widget URL for displaying social stats.

    :param platform: The project's platform.
    :type platform: :class:`.Platform`
    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's Top.gg ID.
    :type id: :py:class:`int`
    :param hide_avatar: Whether to also hide the project's avatar. Defaults to ``False``.
    :type hide_avatar: :py:class:`bool`

    :exception TypeError: The specified platform, project type, and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError(
        "The specified platform, project type, and/or project ID's type is invalid."
      )

    return f'{BASE_URL}/widgets/small/social/{platform.value}/{project_type.value}/{id}{"?hideAvatar=true" if hide_avatar else ""}'
