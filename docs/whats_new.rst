.. currentmodule:: topgg

.. _whats_new:

##########
What's New
##########

This page keeps a detailed human friendly rendering of what's new and changed in specific versions.

v2.0.0
======

Complete rewrite of the SDK for Top.gg API v1.

* New :class:`.Client` class replaces the old ``DBLClient``
* New :class:`.Webhooks` class replaces the old ``WebhookManager``
* New webhook payload classes: :class:`.VoteCreatePayload`, :class:`.TestPayload`, :class:`.IntegrationCreatePayload`, :class:`.IntegrationDeletePayload`
* New :class:`.Project`, :class:`.PartialProject`, :class:`.Announcement`, :class:`.Metrics` data models
* New :class:`.PaginatedVotes` for cursor-based paginated vote retrieval via :meth:`.Client.get_votes`
* New :class:`.Widget` class for generating widget URLs across all platforms and project types
* New :class:`.Platform`, :class:`.ProjectType`, :class:`.PayloadType`, :class:`.UserSource`, :class:`.Locale` enumerations
* No longer depends on any Discord API wrapper
* Per-endpoint rate limiting with :class:`.Ratelimiter`
* Async context manager support on :class:`.Client`

v2.0.0a
=======

* :obj:`~.DBLClient` now doesn't take in ``discord.Client`` instance
* Introduced new `autopost <api/autopost.html>`__ and `data injection <api/data.html>`__ API
* `Webhook <api/webhook.html>`__ API breaking changes
* No longer depends on any Discord API wrapper
* :obj:`~.GuildVoteData` alias

v1.4.0
======

* The type of data passed to ``on_dbl_vote`` has been changed from :class:`dict` to :obj:`BotVoteData`
* The type of data passed to ``on_dsl_vote`` has been changed from :class:`dict` to :obj:`ServerVoteData`

v1.3.0
======

*  Introduced `global ratelimiter <https://docs.top.gg/resources/ratelimits/#global-ratelimit>`__ to follow Top.gg global ratelimits

   *  Fixed an :exc:`AttributeError` raised by :meth:`HTTPClient.request`

   * `Resource-specific ratelimit <https://docs.top.gg/resources/ratelimits/#resource-specific-ratelimits>`__ is now actually resource-specific

v1.2.0
======

* Introduced global ratelimiter along with bot endpoints ratelimiter
* Follow consistency with typing in :class:`HTTPClient` and :class:`DBLClient` along with updated docstrings (:issue:`55`)

v1.1.0
======

*  Introduced `data models <models.html>`__

   * :meth:`DBLClient.get_bot_votes` now returns a list of :class:`BriefUserData` objects

   * :meth:`DBLClient.get_bot_info` now returns a :class:`BotData` object

   * :meth:`DBLClient.get_guild_count` now returns a :class:`BotStatsData` object

   * :meth:`DBLClient.get_user_info` now returns a :class:`UserData` object

* :meth:`WebhookManager.run` now returns an :class:`asyncio.Task`, meaning it can now be optionally awaited

v1.0.1
======

* :attr:`WebhookManager.webserver` now instead returns :class:`aiohttp.web.Application` for ease of use

v1.0.0
======

* Renamed the module folder from ``dbl`` to ``topgg``
* Added ``post_shard_count`` argument to :meth:`DBLClient.post_guild_count`
* Autopost now supports automatic shard posting (:issue:`42`)
*  Large webhook system rework, read the :obj:`api/webhook` section for more

   * Added support for server webhooks

* Renamed ``DBLException`` to :class:`TopGGException`
* Renamed ``DBLClient.get_bot_upvotes()`` to :meth:`DBLClient.get_bot_votes`
* Added :meth:`DBLClient.generate_widget` along with the ``widgets`` section in the documentation
* Implemented a properly working ratelimiter
* Added :func:`on_autopost_error`
* All autopost events now follow ``on_autopost_x`` naming format, e.g. :func:`on_autopost_error`, :func:`on_autopost_success`
* Added handlers for autopost args set when autopost is disabled

v0.4.0
======

* :meth:`DBLClient.post_guild_count` now supports a custom ``guild_count`` argument, which accepts either an integer or list of integers
* Reworked how shard info is posted
* Removed ``InvalidArgument`` and ``ConnectionClosed`` exceptions
* Added ``ServerError`` exception

v0.3.3
======

* Internal changes regarding support of Top.gg migration
* Fixed errors raised when using :meth:`DBLClient.close` without built-in webhook

v0.3.2
======

* ``Client`` class has been renamed to ``DBLClient``

v0.3.1
======

* Added ``on_guild_post``, an event that is called when autoposter successfully posts guild count
* Renamed ``get_upvote_info`` to ``get_bot_upvotes``
* Added ``get_user_vote``

v0.3.0
======

* :class:`DBLClient` now has ``autopost`` kwarg that will post server count automatically every 30 minutes
* Fixed code 403 errors
* Added ``on_dbl_vote``, an event that is called when you test your webhook
* Added ``on_dbl_test``, an event that is called when someone tests your webhook

v0.2.1
======

* Added webhook
* Removed support for discord.py versions lower than 1.0.0
* Made :meth:`DBLClient.get_weekend_status` return a boolean value
* Added webhook example in README
* Removed ``post_server_count`` and ``get_server_count``

v0.2.0
======

*  Added ``post_guild_count``

   * Made ``post_server_count`` an alias for ``post_guild_count``

   * Added ``get_guild_count``

* Made ``get_server_count`` an alias for ``get_guild_count``

* Added :meth:`DBLClient.get_weekend_status`
* Removed all parameters from :meth:`DBLClient.get_upvote_info`
* Added limit to :meth:`DBLClient.get_bots`
* Fixed example in README

v0.1.6
======

* Bug fixes & improvements

v0.1.4
======

* Initial ratelimit handling

v0.1.3
======

* Added documentation
* Fixed some minor bugs

v0.1.2
======

Initial release

* Working

    * POSTing server count
    * GET bot info, server count, upvote count, upvote info
    * GET all bots
    * GET specific user info
    * GET widgets (large and small) including custom ones. See `Top.gg docs <https://docs.top.gg/>`_ for more info.

* Not Working / Implemented

    * Searching for bots via the api
