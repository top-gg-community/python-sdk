.. topggpy documentation master file, created by
   sphinx-quickstart on Thu Feb  8 18:32:44 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================
Top.gg Python SDK
=================

   For more information, see the documentation here: https://topggpy.rtfd.io.

The community-maintained Python SDK for Top.gg.

Installation
------------

.. code-block:: console

   $ pip install topggpy

Setting up
----------

.. code-block:: python

   import topgg

   import os


   token = os.getenv('TOPGG_TOKEN')
   assert token is not None, 'Missing TOPGG_TOKEN environment variable.'

   client = topgg.Client(token)

Usage
-----

Getting your project's information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   project = await client.get_self()

Updating your project's information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   await client.edit_self(headline={
     topgg.Locale.ENGLISH: 'A great bot with tons of features!'
   }, content={
     topgg.Locale.ENGLISH: '# Welcome\nThis is the full page description for your project...'
   })

Getting your project's vote information of a user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Discord ID
^^^^^^^^^^

.. code-block:: python

   vote = await client.get_vote(topgg.UserSource.DISCORD, 661200758510977084)

Top.gg ID
^^^^^^^^^

.. code-block:: python

   vote = await client.get_vote(topgg.UserSource.TOPGG, 8226924471638491136)

Getting a cursor-based paginated list of votes for your project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datetime import datetime


   first_page = await client.get_votes(datetime(2026, 1, 1))

   for vote in first_page:
     print(vote)

   second_page = await first_page.next()

   for vote in second_page:
     print(vote)

   third_page = await second_page.next()

Posting an announcement for your project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   announcement = await client.post_announcement(
     'Version 2.0 Released!',
     'We just released version 2.0 with a bunch of new features and improvements.',
   )

Posting your bot's application commands list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Array of application commands that
   # can be serialized to Discord API's raw JSON format.

   await client.post_commands(
     [
       {
         'id': '1',
         'type': 1,
         'application_id': '1',
         'name': 'test',
         'description': 'command description',
         'default_member_permissions': '',
         'version': '1',
       }
     ]
   )

Posting your project's metric stats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Single
^^^^^^

.. code-block:: python

   await client.post_metrics(topgg.Metrics.discord_bot(server_count=1, shard_count=1))

Batch
^^^^^

.. code-block:: python

   from datetime import datetime


   timestamp1 = datetime.now()
   timestamp2 = datetime.now()

   await client.post_metrics({
     timestamp1: topgg.Metrics.discord_bot(server_count=1, shard_count=1),
     timestamp2: topgg.Metrics.discord_bot(server_count=1, shard_count=1)
   })

Generating widget URLs
~~~~~~~~~~~~~~~~~~~~~~

Large
^^^^^

.. code-block:: python

   widget_url = topgg.Widget.large(topgg.Platform.DISCORD, topgg.ProjectType.BOT, 1026525568344264724)

Votes
^^^^^

.. code-block:: python

   widget_url = topgg.Widget.votes(topgg.Platform.DISCORD, topgg.ProjectType.BOT, 1026525568344264724)

Owner
^^^^^

.. code-block:: python

   widget_url = topgg.Widget.owner(topgg.Platform.DISCORD, topgg.ProjectType.BOT, 1026525568344264724)

Social
^^^^^^

.. code-block:: python

   widget_url = topgg.Widget.social(topgg.Platform.DISCORD, topgg.ProjectType.BOT, 1026525568344264724)

Webhooks
~~~~~~~~

With express:

.. code-block:: python

   import topgg

   from aiohttp import web
   import os


   secret = os.getenv('TOPGG_WEBHOOK_SECRET')
   assert secret is not None, 'Missing TOPGG_WEBHOOK_SECRET environment variable.'

   # POST /webhook
   webhooks = topgg.Webhooks('/webhook', secret)

   @webhooks.on(topgg.PayloadType.TEST)
   async def test_listener(payload: topgg.TestPayload, trace: str) -> web.Response:
     print(payload)

     return web.Response(status=204)

   await webhooks.start()

.. toctree::
   :maxdepth: 2
   :hidden:

   api/index.rst
   webhooks
   support-server
   repository
   raw-api-reference