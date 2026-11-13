.. topggpy documentation master file, created by
   sphinx-quickstart on Thu Feb  8 18:32:44 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================
Top.gg Python SDK
=================

   For more information, see the documentation here: https://topggpy.rtfd.io.

The community-maintained Python library for Top.gg.

Installation
------------

.. code-block:: console

   $ pip install topggpy

Usage
-----

General API calls
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import topgg
   
   from datetime import datetime, timedelta, UTC
   import asyncio
   import os
   
   
   async def main():
     async with topgg.Client(os.getenv('TOPGG_TOKEN')) as client:
       project = await client.get_project()
       print(project)
   
       votes = await client.get_votes(since=datetime.now(UTC) - timedelta(hours=1))
       for vote in votes:
         print(vote)
   
       vote = await client.get_vote(661200758510977084, topgg.UserSource.DISCORD)
       print(vote)
   
       await client.post_announcement(
         'My project announcement',
         'Lorem ipsum' * 25,
         topgg.AnnouncementCategory.ANNOUNCEMENT,
       )
   
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
   
       await client.post_metrics(topgg.DiscordBotMetrics(server_count=5))
   
       headline = topgg.LocaleMap(
         {
           topgg.Locale.ENGLISH: 'hello this is a headline',
           topgg.Locale.GERMAN: 'hallo das ist eine Überschrift',
         }
       )
   
       page_content = topgg.LocaleMap(
         {
           topgg.Locale.ENGLISH: 'hello this is a page content' * 20,
           topgg.Locale.GERMAN: 'hallo dies ist ein seiteninhalt' * 20,
         }
       )
   
       await client.edit_project(headline, page_content)
   
       metrics = topgg.TimestampedMetrics[topgg.DiscordBotMetrics]()
       now = datetime.now(UTC)
   
       metrics.add(now - timedelta(hours=3), topgg.DiscordBotMetrics(server_count=5))
       metrics.add(now - timedelta(hours=2), topgg.DiscordBotMetrics(server_count=6))
       metrics.add(now - timedelta(hours=1), topgg.DiscordBotMetrics(server_count=7))
   
       await client.post_timestamped_metrics(metrics)


   if __name__ == '__main__':
     asyncio.run(main())

aiohttp Webhooks
~~~~~~~~~~~~~~~~

.. code-block:: python

   import topgg
   
   from aiohttp import web
   import asyncio
   import signal
   import json
   import os
   
   
   async def handle_webhooks(request: web.Request) -> web.Response:
     if 'x-topgg-signature' in request.headers and request.can_read_body:
       body = (await request.read()).decode('utf-8')
   
       if topgg.webhooks.verify(
         os.getenv('TOPGG_WEBHOOKS_SECRET'), request.headers['x-topgg-signature'], body
       ):
         payload = topgg.webhooks.parse(json.loads(body))
         print(payload)
   
         return web.Response(status=200, text='OK')
   
     return web.Response(status=401, text='Unauthorized')
   
   
   async def main() -> None:
     app = web.Application()
   
     app.add_routes([web.post('/webhooks', handle_webhooks)])
   
     runner = web.AppRunner(app)
   
     await runner.setup()
   
     site = web.TCPSite(runner, 'localhost', 3000)
   
     await site.start()
   
     stop_event = asyncio.Event()
     loop = asyncio.get_running_loop()
   
     signal.signal(signal.SIGINT, lambda _, __: loop.call_soon_threadsafe(stop_event.set))
   
     try:
       await stop_event.wait()
     finally:
       await runner.cleanup()
   
   
   if __name__ == '__main__':
     asyncio.run(main())

aiohttp Oauth2
~~~~~~~~~~~~~~

.. code-block:: python

   import topgg
   
   from aiohttp import web
   import asyncio
   import signal
   import os
   
   
   async def handle_oauth2(request: web.Request) -> web.Response:
     if (
       'code' in request.query
       and 'state' in request.query
       and f'oauth2_url:{request.query["state"]}' in request.app
     ):
       oauth2: topgg.Oauth2 = request.app['oauth2']
       oauth2_url: topgg.Oauth2URL = request.app[f'oauth2_url:{request.query["state"]}']
   
       try:
         session = await oauth2_url.exchange(request.query['code'])
         client = oauth2.new_client(session)
   
         projects = await client.get_projects()
         integrations = await client.get_integrations(364806029876555776)
         webhooks = await client.get_webhooks(364806029876555776)
   
         user = await client.get_authorized_user()
         user_projects = await client.get_authorized_user_projects()
   
         return web.Response(
           status=200,
           text=f'Projects: {projects!r}\n'
           + f'Integrations: {integrations!r}\n'
           + f'Webhooks: {webhooks!r}\n\n'
           + f'User: {user!r}\n'
           + f'User projects: {user_projects!r}',
         )
       except Exception as err:
         print(err)
         pass
   
     return web.Response(status=401, text='Unauthorized')
   
   
   async def main() -> None:
     app = web.Application()
   
     oauth2 = topgg.Oauth2(
       os.getenv('TOPGG_CLIENT_ID'),
       os.getenv('TOPGG_CLIENT_SECRET'),
       'http://localhost:3000/topgg/oauth2',
       [
         'user.identify',
         'user.projects.read',
         'user.projects.write',
         'project.information.read',
         'project.information.write',
         'project.votes.read',
         'project.metrics.write',
         'project.announcements.write',
         'project.webhooks.read',
         'project.webhooks.write',
         'project.integrations.read',
         'project.integrations.write',
       ],
     )
   
     url = oauth2.new_url()
     print('Please open this URL:', url)
   
     app['oauth2'] = oauth2
     app[f'oauth2_url:{url.state}'] = url
   
     app.add_routes([web.get('/topgg/oauth2', handle_oauth2)])
   
     runner = web.AppRunner(app)
   
     await runner.setup()
   
     site = web.TCPSite(runner, 'localhost', 3000)
   
     await site.start()
   
     stop_event = asyncio.Event()
     loop = asyncio.get_running_loop()
   
     signal.signal(signal.SIGINT, lambda _, __: loop.call_soon_threadsafe(stop_event.set))
   
     try:
       await stop_event.wait()
     finally:
       await runner.cleanup()
       await oauth2.close()
   
   
   if __name__ == '__main__':
     asyncio.run(main())

.. toctree::
   :maxdepth: 2
   :hidden:

   project
   oauth2
   models
   errors
   webhooks
   support-server
   repository
   raw-api-reference