import sys
from datetime import UTC, datetime, timedelta
from os import path
from typing import TYPE_CHECKING

from multidict import CIMultiDict

sys.path.insert(0, path.join(path.dirname(path.realpath(__file__)), '..'))


from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from util import RequestMock, _test_attributes

import topgg


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[topgg.ProjectClient, None]:
  client = topgg.ProjectClient('')

  yield client
  await client.close()


def test_ProjectClient_attributes_work(client: topgg.ProjectClient) -> None:
  _test_attributes(client)


@pytest.mark.asyncio
async def test_ProjectClient_basic_error_handling_works() -> None:
  with pytest.raises(topgg.Error, match=r'^Client session is already closed\.$'):
    test_client = topgg.ProjectClient('')

    await test_client.close()
    await test_client.get_project()


@pytest.mark.asyncio
async def test_ProjectClient_request_error_handling_works(
  monkeypatch: pytest.MonkeyPatch, client: topgg.ProjectClient
) -> None:
  with RequestMock(404, 'Not Found', response='mocks/404_standard.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(topgg.RequestError, match='^Got 404: ') as raises:
      await client.get_project()

    _test_attributes(raises.value)

    request.assert_called_once()

  with RequestMock(
    429, 'Ratelimited', response={}, headers=CIMultiDict({'retry-after': '6000'})
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
async def test_ProjectClient_get_projects_id_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.ProjectClient,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_projects_id.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    project = await client.get_project()
    _test_attributes(project)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_ProjectClient_edit_project_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.ProjectClient,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(
      ValueError, match=r'^A LocaleMap text length is below the minimum range\.$'
    ):
      headline = topgg.LocaleMap(
        {topgg.Locale.ENGLISH: 'hi', topgg.Locale.GERMAN: 'hi'}
      )

      page_content = topgg.LocaleMap(
        {topgg.Locale.ENGLISH: 'hi', topgg.Locale.GERMAN: 'hi'}
      )

      await client.edit_project(headline, page_content)

    if not TYPE_CHECKING:
      with pytest.raises(TypeError, match=r'^The specified locale must be a Locale\.$'):
        headline = topgg.LocaleMap(
          {
            'ENGLISH': 'hello this is a headline',
            'GERMAN': 'hallo das ist eine Überschrift',
          }
        )

        page_content = topgg.LocaleMap(
          {
            'ENGLISH': 'hello this is a page content' * 20,
            'GERMAN': 'hallo dies ist ein seiteninhalt' * 20,
          }
        )

        await client.edit_project(headline, page_content)

      with pytest.raises(TypeError, match=r'^The specified text must be a string\.$'):
        headline = topgg.LocaleMap(
          {topgg.Locale.ENGLISH: [None] * 100, topgg.Locale.GERMAN: [None] * 100}
        )

        page_content = topgg.LocaleMap(
          {topgg.Locale.ENGLISH: [None] * 100, topgg.Locale.GERMAN: [None] * 100}
        )

        await client.edit_project(headline, page_content)

    headline = topgg.LocaleMap(
      {
        topgg.Locale.ENGLISH: 'hello this is a headline',
        topgg.Locale.GERMAN: 'hallo das ist eine Überschrift',
      }
    )
    _test_attributes(headline)

    page_content = topgg.LocaleMap(
      {
        topgg.Locale.ENGLISH: 'hello this is a page content' * 20,
        topgg.Locale.GERMAN: 'hallo dies ist ein seiteninhalt' * 20,
      }
    )

    await client.edit_project(headline, page_content)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_ProjectClient_post_announcement_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.ProjectClient,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(
      ValueError, match=r'^Title length is outside of the accepted range\.$'
    ):
      await client.post_announcement(
        '', 'Lorem ipsum' * 25, topgg.AnnouncementCategory.ANNOUNCEMENT
      )

    with pytest.raises(
      ValueError, match=r'^Content length is outside of the accepted range\.$'
    ):
      await client.post_announcement(
        'My project announcement',
        'Lorem ipsum',
        topgg.AnnouncementCategory.ANNOUNCEMENT,
      )

    await client.post_announcement(
      'My project announcement',
      'Lorem ipsum' * 25,
      topgg.AnnouncementCategory.ANNOUNCEMENT,
    )

    request.assert_called_once()


@pytest.mark.asyncio
async def test_ProjectClient_post_metrics_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.ProjectClient,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(
      ValueError, match=r'^The server count and\/or shard count must be specified\.$'
    ):
      await client.post_metrics(topgg.DiscordBotMetrics())

    if not TYPE_CHECKING:
      with pytest.raises(
        TypeError, match=r'^The specified server count must be an integer\.$'
      ):
        await client.post_metrics(topgg.DiscordBotMetrics(server_count=''))

      with pytest.raises(
        TypeError, match=r'^The specified shard count must be an integer\.$'
      ):
        await client.post_metrics(topgg.DiscordBotMetrics(shard_count=''))

    metrics = topgg.DiscordBotMetrics(server_count=5)
    _test_attributes(metrics)

    await client.post_metrics(metrics)
    await client.post_metrics(topgg.DiscordBotMetrics(shard_count=5))

    with pytest.raises(
      ValueError,
      match=r'^The total member count and\/or online member count must be specified\.$',
    ):
      await client.post_metrics(topgg.DiscordServerMetrics())

    if not TYPE_CHECKING:
      with pytest.raises(
        TypeError, match=r'^The specified total member count must be an integer\.$'
      ):
        await client.post_metrics(topgg.DiscordServerMetrics(member_count=''))

      with pytest.raises(
        TypeError, match=r'^The specified online member count must be an integer\.$'
      ):
        await client.post_metrics(topgg.DiscordServerMetrics(online_count=''))

    metrics = topgg.DiscordServerMetrics(member_count=5)
    _test_attributes(metrics)

    await client.post_metrics(metrics)
    await client.post_metrics(topgg.DiscordServerMetrics(online_count=5))

    if not TYPE_CHECKING:
      with pytest.raises(
        TypeError, match=r'^The specified player count must be an integer\.$'
      ):
        await client.post_metrics(topgg.RobloxGameMetrics(''))

    metrics = topgg.RobloxGameMetrics(player_count=5)
    _test_attributes(metrics)

    await client.post_metrics(metrics)

    assert request.call_count == 5


@pytest.mark.asyncio
async def test_ProjectClient_post_timestamped_metrics_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.ProjectClient,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    metrics = topgg.TimestampedMetrics[topgg.DiscordBotMetrics]()
    now = datetime.now(UTC)

    with pytest.raises(
      ValueError, match=r'^Batch length is outside of the accepted range\.$'
    ):
      await client.post_timestamped_metrics(metrics)

    metrics.add(now - timedelta(hours=3), topgg.DiscordBotMetrics(server_count=5))
    metrics.add(now - timedelta(hours=2), topgg.DiscordBotMetrics(server_count=6))
    metrics.add(now - timedelta(hours=1), topgg.DiscordBotMetrics(server_count=7))

    _test_attributes(metrics)

    if not TYPE_CHECKING:
      with pytest.raises(
        TypeError, match=r'^The specified timestamp must be a datetime\.$'
      ):
        metrics.add(1, topgg.DiscordBotMetrics(server_count=7))

      with pytest.raises(
        TypeError, match=r'^The specified metrics must be a child of Metrics\.$'
      ):
        metrics.add(now - timedelta(hours=1), topgg.TimestampedMetrics())

    await client.post_timestamped_metrics(metrics)

    metrics.clear()

    assert len(metrics._json) == 0
    request.assert_called_once()


@pytest.mark.asyncio
async def test_ProjectClient_post_commands_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.ProjectClient,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

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

    request.assert_called_once()


@pytest.mark.asyncio
async def test_ProjectClient_get_votes_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.ProjectClient,
) -> None:
  with RequestMock(
    200, 'OK', response='mocks/get_projects_id_votes_cursor.json'
  ) as request:
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

  with RequestMock(200, 'OK', response='mocks/get_projects_id_votes.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(
      topgg.Error, match=r'^The reference is already on the last page\.$'
    ):
      votes = await client.get_votes(since=datetime.now(UTC) - timedelta(hours=1))

      request.assert_called_once()

      await client.get_votes(reference=votes)


@pytest.mark.asyncio
async def test_ProjectClient_get_vote_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.ProjectClient,
) -> None:
  with RequestMock(
    200, 'OK', response='mocks/get_projects_id_votes_id.json'
  ) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    vote = await client.get_vote(661200758510977084, topgg.UserSource.DISCORD)

    _test_attributes(vote)

    request.assert_called_once()

  with RequestMock(404, 'Not Found', response='mocks/404_not_voted.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    vote = await client.get_vote(661200758510977084, topgg.UserSource.DISCORD)

    assert vote is None

    request.assert_called_once()
