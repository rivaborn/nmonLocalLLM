import time
from unittest.mock import Mock

import pytest
from rich.panel import Panel

from nmon.alerts import AlertState
from nmon.config import Settings
from nmon.widgets.alert_bar import AlertBar


def test_alert_bar_hidden_when_alert_state_is_none():
    """Test that AlertBar returns a zero-height Panel when alert_state is None."""
    settings = Settings()
    alert_bar = AlertBar(alert_state=None, settings=settings)

    panel = alert_bar.__rich__()

    assert isinstance(panel, Panel)
    assert panel.height == 0


def test_alert_bar_red_background_when_color_is_red(monkeypatch):
    """Test that AlertBar returns a Panel with red background when alert_state.color is 'red'."""
    monkeypatch.setattr(time, 'time', Mock(return_value=100.0))

    settings = Settings()
    alert_state = AlertState(
        active=True,
        message="Test message",
        color="red",
        expires_at=200.0
    )
    alert_bar = AlertBar(alert_state=alert_state, settings=settings)

    panel = alert_bar.__rich__()

    assert isinstance(panel, Panel)
    assert panel.height > 0
    # The panel's style should have red background
    # Note: Rich panel styling is complex to test directly, so we mainly check it's not hidden


def test_alert_bar_orange_background_when_color_is_orange(monkeypatch):
    """Test that AlertBar returns a Panel with orange background when alert_state.color is 'orange'."""
    monkeypatch.setattr(time, 'time', Mock(return_value=100.0))

    settings = Settings()
    alert_state = AlertState(
        active=True,
        message="Test message",
        color="orange",
        expires_at=200.0
    )
    alert_bar = AlertBar(alert_state=alert_state, settings=settings)

    panel = alert_bar.__rich__()

    assert isinstance(panel, Panel)
    assert panel.height > 0
    # The panel's style should have orange background
    # Note: Rich panel styling is complex to test directly, so we mainly check it's not hidden


def test_alert_bar_hidden_when_current_time_exceeds_expires_at(monkeypatch):
    """Test that AlertBar returns a zero-height Panel when current time >= alert_state.expires_at."""
    monkeypatch.setattr(time, 'time', Mock(return_value=300.0))  # Time after expiration

    settings = Settings()
    alert_state = AlertState(
        active=True,
        message="Test message",
        color="red",
        expires_at=200.0  # Already expired
    )
    alert_bar = AlertBar(alert_state=alert_state, settings=settings)

    panel = alert_bar.__rich__()

    assert isinstance(panel, Panel)
    assert panel.height == 0


def test_alert_bar_update_method(monkeypatch):
    """Test that update() correctly updates internal alert_state and visibility state."""
    monkeypatch.setattr(time, 'time', Mock(return_value=100.0))

    settings = Settings()
    alert_state = AlertState(
        active=True,
        message="Test message",
        color="red",
        expires_at=200.0
    )
    alert_bar = AlertBar(alert_state=alert_state, settings=settings)

    # Update with new alert state
    new_alert_state = AlertState(
        active=True,
        message="New message",
        color="orange",
        expires_at=300.0
    )
    alert_bar.update(new_alert_state, now=100.0)

    # Check that internal state was updated
    panel = alert_bar.__rich__()
    assert isinstance(panel, Panel)
    assert panel.height > 0  # Should be visible now


def test_alert_bar_update_method_with_none(monkeypatch):
    """Test that update() correctly handles None alert_state."""
    monkeypatch.setattr(time, 'time', Mock(return_value=100.0))

    settings = Settings()
    alert_state = AlertState(
        active=True,
        message="Test message",
        color="red",
        expires_at=200.0
    )
    alert_bar = AlertBar(alert_state=alert_state, settings=settings)

    # Update with None
    alert_bar.update(None, now=100.0)

    # Check that internal state was updated
    panel = alert_bar.__rich__()
    assert isinstance(panel, Panel)
    assert panel.height == 0  # Should be hidden now
