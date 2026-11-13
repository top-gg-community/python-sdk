# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

import hashlib
import hmac
from time import time

from ..errors import Error
from .models import IntegrationCreate, IntegrationDelete, Test, VoteCreate

Payload = VoteCreate | Test | IntegrationCreate | IntegrationDelete
"""A webhook payload."""


def parse(json: dict) -> Payload:
  """
  Parses a webhook request's JSON body.

  :param json: The webhook request's JSON body.
  :type json: :py:class:`dict`

  :exception Error: The webhook payload is unrecognized.

  :returns: The parsed webhook payload.
  :rtype: :class:`.Payload`
  """

  type_ = json.get('type')
  data = json.get('data')

  if data is None:
    raise Error('Missing data property.')

  match type_:
    case 'vote.create':
      return VoteCreate(data)
    case 'webhook.test':
      return Test(data)
    case 'integration.create':
      return IntegrationCreate(data)
    case 'integration.delete':
      return IntegrationDelete(data)
    case _:
      raise Error('Unrecognized webhook payload type.')


def verify(secret: str, signature: str, body: str) -> bool:
  """
  Verifies an incoming webhook request.

  :param secret: The webhook's current secret.
  :type secret: :py:class:`str`
  :param signature: The request's x-topgg-signature header.
  :type signature: :py:class:`str`
  :param body: The request's raw body.
  :type body: :py:class:`str`

  :exception Error: The webhook payload's event type is unrecognized.

  :returns: Whether the request is authorized.
  :rtype: :py:class:`bool`
  """

  parts = signature.split(',')

  if len(parts) != 2:
    return False

  try:
    timestamp = int(parts[0].split('=')[1])
    received_signature = parts[1].split('=')[1].encode('utf-8')

    if abs(time() - timestamp) > 300:
      return False

    expected_signature = (
      hmac.new(secret.encode('utf-8'), f'{timestamp}.{body}'.encode(), hashlib.sha256)
      .hexdigest()
      .encode('utf-8')
    )

    if len(expected_signature) != len(received_signature):
      return False

    return hmac.compare_digest(expected_signature, received_signature)
  except (IndexError, ValueError):
    return False
