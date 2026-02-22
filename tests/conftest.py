"""Shared fixtures for warpgate tests."""

import importlib
import os
import sys

import pytest

# ---------------------------------------------------------------------------
# Path bootstrap: make module_utils/warpgate_client importable both as
# `warpgate_client` (direct) AND as `ansible.module_utils.warpgate_client`
# (the path used inside library/*.py modules).
# ---------------------------------------------------------------------------

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_module_utils = os.path.join(_root, "module_utils")
_library = os.path.join(_root, "library")

if _module_utils not in sys.path:
    sys.path.insert(0, _module_utils)
if _library not in sys.path:
    sys.path.insert(0, _library)

# Register warpgate_client package under the ansible.module_utils namespace
# so that library modules can ``from ansible.module_utils.warpgate_client import …``.
# Ansible is expected to be installed (via devbox) so we don't stub it.
_pkg = importlib.import_module("warpgate_client")
sys.modules["ansible.module_utils.warpgate_client"] = _pkg
import ansible.module_utils  # noqa: E402

ansible.module_utils.warpgate_client = _pkg  # type: ignore[attr-defined]

for _sub in ("client", "user", "role", "credential", "target", "target_group", "ticket", "helpers"):
    _mod = importlib.import_module(f"warpgate_client.{_sub}")
    sys.modules[f"ansible.module_utils.warpgate_client.{_sub}"] = _mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock  # noqa: E402

from warpgate_client.client import WarpgateClient  # noqa: E402


@pytest.fixture
def mock_client():
    """A WarpgateClient whose network layer (_request) is mocked."""
    client = MagicMock(spec=WarpgateClient)
    client._request = MagicMock()
    return client


@pytest.fixture
def mock_module():
    """A minimal AnsibleModule mock with check_mode=False."""
    module = MagicMock()
    module.check_mode = False
    module.debug = MagicMock()
    module.fail_json = MagicMock(side_effect=SystemExit)
    return module
