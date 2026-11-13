from datetime import datetime, UTC
from os import path
import hashlib
import hmac
import json
import sys

CURRENT_DIR = path.dirname(path.realpath(__file__))
sys.path.insert(0, path.join(CURRENT_DIR, '..'))


import pytest

import topgg

from util import _test_attributes


def test_webhooks_parse_works() -> None:
  with open(path.join(CURRENT_DIR, './mocks/vote_create_payload.json'), 'r') as raw_payload:
    payload = topgg.webhooks.parse(json.loads(raw_payload.read()))

    assert isinstance(payload, topgg.webhooks.VoteCreate)
    _test_attributes(payload)

  with open(path.join(CURRENT_DIR, './mocks/test_payload.json'), 'r') as raw_payload:
    payload = topgg.webhooks.parse(json.loads(raw_payload.read()))

    assert isinstance(payload, topgg.webhooks.Test)
    _test_attributes(payload)

  with open(path.join(CURRENT_DIR, './mocks/integration_create_payload.json'), 'r') as raw_payload:
    payload = topgg.webhooks.parse(json.loads(raw_payload.read()))

    assert isinstance(payload, topgg.webhooks.IntegrationCreate)
    _test_attributes(payload)

  with open(path.join(CURRENT_DIR, './mocks/integration_delete_payload.json'), 'r') as raw_payload:
    payload = topgg.webhooks.parse(json.loads(raw_payload.read()))

    assert isinstance(payload, topgg.webhooks.IntegrationDelete)
    _test_attributes(payload)

  with pytest.raises(topgg.Error, match=r'^Missing data property\.$'):
    topgg.webhooks.parse({})

  with pytest.raises(topgg.Error, match=r'^Unrecognized webhook payload type\.$'):
    topgg.webhooks.parse({'type': '', 'data': {}})

def test_webhooks_verify_works() -> None:
  now = round(datetime.now(UTC).timestamp())
  body = '{"type":"webhook.test","data":{"user":{"id":"8226924471638491136","platform_id":"661200758510977084","name":"null8626","avatar_url":"https://cdn.discordapp.com/avatars/661200758510977084/4354318859c319c7ca39753260fdd350.png"},"project":{"id":"364806029876555776","type":"bot","platform":"discord","platform_id":"1026525568344264724"}}}'
  expected_signature = hmac.new(b'abcdefghijklmnopqrstuvwxyz', str(now).encode() + b'.' + body.encode(), hashlib.sha256).hexdigest()

  assert not topgg.webhooks.verify('abcdefghijklmnopqrstuvwxyz', '', body)
  assert not topgg.webhooks.verify('abcdefghijklmnopqrstuvwxyz', f't={now - 400},v1={expected_signature}', body)
  assert not topgg.webhooks.verify('abcdefghijklmnopqrstuvwxyz', f't={now},v1={expected_signature[:10]}', body)
  assert not topgg.webhooks.verify('abcdefghijklmnopqrstuvwxyz', f't=,v1={expected_signature}', body)

  assert topgg.webhooks.verify('abcdefghijklmnopqrstuvwxyz', f't={now},v1={expected_signature}', body)