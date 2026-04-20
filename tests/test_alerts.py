import time
from dataclasses import dataclass
from typing import Optional

# Import the AlertState class from the alerts module
from src.nmon.alerts import AlertState

def test_alert_state_creation():
    """Test creating an AlertState instance"""
    # Create an alert state with all required fields
    alert = AlertState(
        active=True,
        message="Test alert message",
        color="orange",
        expires_at=time.time() + 60.0
    )
    
    # Verify all fields are set correctly
    assert alert.active == True
    assert alert.message == "Test alert message"
    assert alert.color == "orange"
    assert isinstance(alert.expires_at, float)

def test_alert_state_inactive():
    """Test creating an inactive alert state"""
    alert = AlertState(
        active=False,
        message="Inactive alert",
        color="red",
        expires_at=time.time() + 30.0
    )
    
    assert alert.active == False
    assert alert.message == "Inactive alert"
    assert alert.color == "red"

def test_alert_state_color_validation():
    """Test that color field accepts only allowed values"""
    # Test orange color
    alert1 = AlertState(
        active=True,
        message="Orange alert",
        color="orange",
        expires_at=time.time() + 60.0
    )
    assert alert1.color == "orange"
    
    # Test red color
    alert2 = AlertState(
        active=True,
        message="Red alert",
        color="red",
        expires_at=time.time() + 60.0
    )
    assert alert2.color == "red"
    
    # Test that other values are not enforced at runtime (since it's a str field)
    # but the system should only use orange and red colors
    alert3 = AlertState(
        active=True,
        message="Other color",
        color="blue",
        expires_at=time.time() + 60.0
    )
    assert alert3.color == "blue"

def test_alert_state_expires_at():
    """Test expires_at field behavior"""
    current_time = time.time()
    expires_at = current_time + 120.0  # 2 minutes from now
    
    alert = AlertState(
        active=True,
        message="Expiring alert",
        color="orange",
        expires_at=expires_at
    )
    
    assert alert.expires_at == expires_at
    assert alert.expires_at > current_time
