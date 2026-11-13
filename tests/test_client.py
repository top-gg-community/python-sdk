from datetime import datetime, timedelta, UTC
from multidict import CIMultiDict
from typing import TYPE_CHECKING
from os import path
import sys

sys.path.insert(0, path.join(path.dirname(path.realpath(__file__)), '..'))


from typing import AsyncGenerator
import pytest_asyncio
import pytest

import topgg

from util import _test_attributes, RequestMock


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[topgg.Client, None]:
  client = topgg.Client('')

  yield client
  await client.close()


def test_Client_attributes_work(client: topgg.Client) -> None:
  _test_attributes(client)
  _test_attributes(client._http)


@pytest.mark.asyncio
async def test_Client_basic_error_handling_works() -> None:
  with pytest.raises(topgg.Error, match='^Client session is already closed.$'):
    test_client = topgg.Client('')

    await test_client.close()
    await test_client.get_project()


@pytest.mark.asyncio
async def test_Client_request_error_handling_works(
  monkeypatch: pytest.MonkeyPatch, client: topgg.Client
) -> None:
  with RequestMock(404, 'Not Found', response='mocks/404.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(topgg.RequestError, match='^Got 404: ') as raises:
      await client.get_project()

    _test_attributes(raises.value)

    request.assert_called_once()

  with RequestMock(
    429, 'Ratelimited', response={}, headers=CIMultiDict({'Retry-After': '6000'})
  ) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    for _ in range(2):
      with pytest.raises(
        topgg.Ratelimited,
        match='^The client is blocked by the API. Please try again in ',
      ) as raises:
        await client.get_project()

      _test_attributes(raises.value)
      assert 0 <= (6000.0 - raises.value.retry_after) < 0.01

    assert request.call_count == 2


@pytest.mark.asyncio
async def test_Client_get_projects_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_projects.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    projects = await client.get_projects()
    _test_attributes(projects)

    for project in projects:
      _test_attributes(project)

    await client.get_projects(projects)

    assert request.call_count == 2


@pytest.mark.asyncio
async def test_Client_get_projects_id_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_projects_id.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    project = await client.get_project()
    _test_attributes(project)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_edit_project_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(ValueError, match=r'^A LocaleMap text length is below the minimum threshold\.$'):
      headline = topgg.LocaleMap({
        topgg.Locale.ENGLISH: 'hi',
        topgg.Locale.GERMAN: 'hi'
      })

      page_content = topgg.LocaleMap({
        topgg.Locale.ENGLISH: 'hi',
        topgg.Locale.GERMAN: 'hi'
      })

      await client.edit_project(headline, page_content)

    if not TYPE_CHECKING:
      with pytest.raises(TypeError, match=r'^The specified locale must be a Locale\.$'):
        headline = topgg.LocaleMap({
          'ENGLISH': 'hello this is a headline',
          'GERMAN': 'hallo das ist eine Überschrift'
        })

        page_content = topgg.LocaleMap({
          'ENGLISH': 'hello this is a page content' * 20,
          'GERMAN': 'hallo dies ist ein seiteninhalt' * 20
        })

        await client.edit_project(headline, page_content)

      with pytest.raises(TypeError, match=r'^The specified text must be a string\.$'):
        headline = topgg.LocaleMap({
          topgg.Locale.ENGLISH: [None] * 100,
          topgg.Locale.GERMAN: [None] * 100
        })

        page_content = topgg.LocaleMap({
          topgg.Locale.ENGLISH: [None] * 100,
          topgg.Locale.GERMAN: [None] * 100
        })

        await client.edit_project(headline, page_content)

    headline = topgg.LocaleMap({
      topgg.Locale.ENGLISH: 'hello this is a headline',
      topgg.Locale.GERMAN: 'hallo das ist eine Überschrift'
    })
    _test_attributes(headline)

    page_content = topgg.LocaleMap({
      topgg.Locale.ENGLISH: 'hello this is a page content' * 20,
      topgg.Locale.GERMAN: 'hallo dies ist ein seiteninhalt' * 20
    })

    await client.edit_project(headline, page_content)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_post_announcement_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(ValueError, match=r'^Title length is outside of the accepted threshold\.$'):
      await client.post_announcement('', 'Lorem ipsum' * 25, topgg.AnnouncementCategory.ANNOUNCEMENT)

    with pytest.raises(ValueError, match=r'^Content length is outside of the accepted threshold\.$'):
      await client.post_announcement('My project announcement', 'Lorem ipsum', topgg.AnnouncementCategory.ANNOUNCEMENT)

    await client.post_announcement('My project announcement', 'Lorem ipsum' * 25, topgg.AnnouncementCategory.ANNOUNCEMENT)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_post_metrics_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(ValueError, match=r'^The server count and\/or shard count must be specified\.$'):
      await client.post_metrics(topgg.DiscordBotMetrics())

    if not TYPE_CHECKING:
      with pytest.raises(TypeError, match=r'^The specified server count must be an integer\.$'):
        await client.post_metrics(topgg.DiscordBotMetrics(server_count=''))

      with pytest.raises(TypeError, match=r'^The specified shard count must be an integer\.$'):
        await client.post_metrics(topgg.DiscordBotMetrics(shard_count=''))

    metrics = topgg.DiscordBotMetrics(server_count=5)
    _test_attributes(metrics)

    await client.post_metrics(metrics)
    await client.post_metrics(topgg.DiscordBotMetrics(shard_count=5))

    with pytest.raises(ValueError, match=r'^The total member count and\/or online member count must be specified\.$'):
      await client.post_metrics(topgg.DiscordServerMetrics())

    if not TYPE_CHECKING:
      with pytest.raises(TypeError, match=r'^The specified total member count must be an integer\.$'):
        await client.post_metrics(topgg.DiscordServerMetrics(total_member_count=''))

      with pytest.raises(TypeError, match=r'^The specified online member count must be an integer\.$'):
        await client.post_metrics(topgg.DiscordServerMetrics(online_member_count=''))

    metrics = topgg.DiscordServerMetrics(total_member_count=5)
    _test_attributes(metrics)

    await client.post_metrics(metrics)
    await client.post_metrics(topgg.DiscordServerMetrics(online_member_count=5))

    if not TYPE_CHECKING:
      with pytest.raises(TypeError, match=r'^The specified player count must be an integer\.$'):
        await client.post_metrics(topgg.RobloxGameMetrics(''))

    metrics = topgg.RobloxGameMetrics(player_count=5)
    _test_attributes(metrics)

    await client.post_metrics(metrics)

    assert request.call_count == 5


@pytest.mark.asyncio
async def test_Client_post_timestamped_metrics_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    metrics = topgg.TimestampedMetrics[topgg.DiscordBotMetrics]()
    now = datetime.now(UTC)

    with pytest.raises(ValueError, match=r'^Batch length is outside of the accepted threshold\.$'):
      await client.post_timestamped_metrics(metrics)

    metrics.add(now - timedelta(hours=3), topgg.DiscordBotMetrics(server_count=5))
    metrics.add(now - timedelta(hours=2), topgg.DiscordBotMetrics(server_count=6))
    metrics.add(now - timedelta(hours=1), topgg.DiscordBotMetrics(server_count=7))

    _test_attributes(metrics)

    if not TYPE_CHECKING:
      with pytest.raises(TypeError, match=r'^The specified timestamp must be a datetime\.$'):
        metrics.add(1, topgg.DiscordBotMetrics(server_count=7))

      with pytest.raises(TypeError, match=r'^The specified metrics must be a child of Metrics\.$'):
        metrics.add(now - timedelta(hours=1), topgg.TimestampedMetrics())

    await client.post_timestamped_metrics(metrics)

    metrics.clear()

    assert len(metrics._json) == 0
    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_post_commands_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.post_commands([{'id':'1','type':1,'application_id':'1','name':'test','description':'command description','default_member_permissions':'','version':'1'}])

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_get_votes_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_projects_id_votes.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(ValueError, match=r'^Missing required arguments\.$'):
      await client.get_votes()

    with pytest.raises(ValueError, match=r'^Invalid since timestamp\.$'):
      await client.get_votes(since=datetime.now(UTC) + timedelta(hours=1))

    votes = await client.get_votes(since=datetime.now(UTC) - timedelta(hours=1))
    _test_attributes(votes)

    for vote in votes:
      _test_attributes(vote)

    await client.get_votes(reference=votes)

    assert request.call_count == 2


@pytest.mark.asyncio
async def test_Client_get_vote_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_projects_id_votes_id.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    vote = await client.get_vote(661200758510977084, topgg.UserSource.DISCORD)

    _test_attributes(vote)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_get_integrations_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_projects_id_integrations.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    integrations = await client.get_integrations(364806029876555776)
    _test_attributes(integrations)

    for integration in integrations:
      _test_attributes(integration)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_connect_integration_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.connect_integration(364806029876555776, 364806029876555776)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_disconnect_integration_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.disconnect_integration(364806029876555776, 364806029876555776)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_get_webhooks_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_projects_id_webhooks.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    webhooks = await client.get_webhooks(364806029876555776)
    _test_attributes(webhooks)

    for webhook in webhooks:
      _test_attributes(webhook)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_create_webhook_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/post_projects_id_webhooks.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    webhook = topgg.BaseWebhook(label='test webhook', url='http://localhost:3000/webhooks')
    _test_attributes(webhook)

    created_webhook = await client.create_webhook(364806029876555776, webhook)
    _test_attributes(created_webhook)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_delete_webhook_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.delete_webhook(364806029876555776, 364806029876555776)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_rotate_webhook_secret_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/post_projects_id_webhooks_id_rotate.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    secret = await client.rotate_webhook_secret(364806029876555776, 364806029876555776)

    assert isinstance(secret, str) and len(secret) > 0
    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_test_webhook_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.test_webhook(364806029876555776, 364806029876555776)

    request.assert_called_once()