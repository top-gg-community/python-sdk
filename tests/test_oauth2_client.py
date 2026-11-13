from os import path
import sys

sys.path.insert(0, path.join(path.dirname(path.realpath(__file__)), '..'))


from typing import AsyncGenerator
import pytest_asyncio
import pytest

import topgg

from util import _test_attributes, RequestMock


@pytest_asyncio.fixture
async def oauth2() -> AsyncGenerator[topgg.Oauth2, None]:
  manager = topgg.Oauth2(
    '',
    '',
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

  yield manager
  await manager.close()


@pytest_asyncio.fixture
async def client(oauth2: topgg.Oauth2) -> topgg.Oauth2Client:
  return oauth2.new_client(topgg.Oauth2Session('', ''))


def test_Oauth2_attributes_work(oauth2: topgg.Oauth2) -> None:
  _test_attributes(oauth2)


def test_Oauth2_new_url_works(oauth2: topgg.Oauth2) -> None:
  url = oauth2.new_url()
  _test_attributes(url)
  assert isinstance(url.url, str) and len(url.url) > 0


@pytest.mark.asyncio
async def test_Oauth2_has_expired_works(client: topgg.Oauth2Client) -> None:
  assert not await client.has_expired()


@pytest.mark.asyncio
async def test_Oauth2_exchange_works(
  monkeypatch: pytest.MonkeyPatch,
  oauth2: topgg.Oauth2,
) -> None:
  with RequestMock(200, 'OK', response='mocks/post_oauth2_token.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    url = oauth2.new_url()
    session = await url.exchange('')
    _test_attributes(session)

    client = oauth2.new_client(topgg.Oauth2Session('', ''))
    _test_attributes(client)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Oauth2_get_authorized_user_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Oauth2Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_users_me.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    user = await client.get_authorized_user()
    _test_attributes(user)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Oauth2_get_authorized_user_projects_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Oauth2Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_users_me_projects.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    projects = await client.get_authorized_user_projects()
    _test_attributes(projects)

    for project in projects:
      _test_attributes(project)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Oauth2_submit_project_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Oauth2Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(
      ValueError, match=r'^Headline length is outside of the accepted threshold\.$'
    ):
      submission = topgg.ProjectSubmission(
        platform=topgg.Platform.DISCORD,
        type=topgg.ProjectType.BOT,
        platform_id=1557409617225457727,
        headline='hi',
        page_content='hello this is a page content' * 20,
      )

      await client.submit_project(submission)

    with pytest.raises(
      ValueError, match=r'^Page content length is outside of the accepted threshold\.$'
    ):
      submission = topgg.ProjectSubmission(
        platform=topgg.Platform.DISCORD,
        type=topgg.ProjectType.BOT,
        platform_id=1557409617225457727,
        headline='hello this is a headline',
        page_content='hello',
      )

      await client.submit_project(submission)

    submission = topgg.ProjectSubmission(
      platform=topgg.Platform.DISCORD,
      type=topgg.ProjectType.BOT,
      platform_id=1557409617225457727,
      headline='hello this is a headline',
      page_content='hello this is a page content' * 20,
    )
    _test_attributes(submission)

    await client.submit_project(submission)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Oauth2_refresh_token_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Oauth2Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/post_oauth2_token.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client._refresh_token()

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Oauth2_revoke_token_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Oauth2Client,
) -> None:
  with RequestMock(204, 'No Content', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.revoke_token()

    request.assert_called_once()
