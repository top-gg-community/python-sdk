import sys
from os import path

sys.path.insert(0, path.join(path.dirname(path.realpath(__file__)), '..'))


import pytest

import topgg


@pytest.mark.parametrize('function_name', ('large', 'votes', 'owner', 'social'))
@pytest.mark.parametrize('platform', tuple(iter(topgg.Platform)))
@pytest.mark.parametrize('project_type', tuple(iter(topgg.ProjectType)))
@pytest.mark.parametrize('hide_avatar', (True, False))
def test_Widget_works(
  function_name: str,
  platform: topgg.Platform,
  project_type: topgg.ProjectType,
  hide_avatar: bool,
):
  function = getattr(topgg.Widget, function_name)

  url = function(platform, project_type, 123456, hide_avatar=hide_avatar)
  path = 'large' if function_name == 'large' else f'small/{function_name}'

  assert (
    url
    == f'{topgg.client.BASE_URL}/widgets/{path}/{platform.value}/{project_type.value}/123456{"?hideAvatar=true" if hide_avatar else ""}'
  )

  with pytest.raises(
    TypeError,
    match=r'^The specified platform, project type, and/or project ID\'s type is invalid.$',
  ):
    function(platform, project_type, None)
