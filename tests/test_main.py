import pytest
import panel as pn
import pandas as pd
from unittest.mock import MagicMock, patch

# Function to test
from app.main import create_sales_dashboard, MockUser # Assuming MockUser is in main for current_user

# Mock the hana_connector module to avoid actual DB calls
# We will mock its functions directly in tests.

@pytest.fixture
def mock_user():
    """Fixture for a mock user object."""
    return MockUser(username="testuser")

@pytest.fixture
def mock_hana_connection_success(mocker):
    """Mocks a successful HANA connection."""
    mock_conn = MagicMock()
    mocker.patch('app.main.hana_connector.get_hana_connection', return_value=mock_conn)
    return mock_conn

@pytest.fixture
def mock_get_sales_data_success(mocker):
    """Mocks successful sales data fetching."""
    mock_df = pd.DataFrame({'Sales': [100, 200], 'Product': ['A', 'B']})
    mocker.patch('app.main.hana_connector.get_sales_data', return_value=mock_df)
    return mock_df

@pytest.fixture
def mock_hana_connection_failure(mocker):
    """Mocks a failed HANA connection (returns None)."""
    mocker.patch('app.main.hana_connector.get_hana_connection', return_value=None)

@pytest.fixture
def mock_hana_connection_exception(mocker):
    """Mocks a failed HANA connection (raises Exception)."""
    mocker.patch('app.main.hana_connector.get_hana_connection', side_effect=Exception("Connection Failed Error"))


def test_create_sales_dashboard_success(mock_user, mock_hana_connection_success, mock_get_sales_data_success):
    """
    Test create_sales_dashboard when HANA connection and data fetching are successful.
    """
    dashboard = create_sales_dashboard(user=mock_user)

    assert isinstance(dashboard, pn.layout.Columnable) # Check if it's a Panel Column or similar layout

    # Check for specific components, e.g., DataFrame
    found_dataframe = False
    found_success_alert = False
    for item in dashboard:
        if isinstance(item, pn.pane.DataFrame):
            found_dataframe = True
            assert item.object is mock_get_sales_data_success # Check if the correct DataFrame is displayed
        if isinstance(item, pn.pane.Alert) and item.alert_type == 'success':
            found_success_alert = True
            assert "Successfully connected" in item.object
            
    assert found_dataframe, "Dashboard should contain a DataFrame pane for sales data."
    assert found_success_alert, "Dashboard should show a success alert for HANA connection."
    
    # Ensure get_hana_connection and get_sales_data were called
    app.main.hana_connector.get_hana_connection.assert_called_once()
    app.main.hana_connector.get_sales_data.assert_called_once_with(mock_hana_connection_success)
    
    # Ensure connection close was attempted
    mock_hana_connection_success.close.assert_called_once()


def test_create_sales_dashboard_connection_returns_none(mock_user, mock_hana_connection_failure):
    """
    Test create_sales_dashboard when get_hana_connection returns None.
    """
    dashboard = create_sales_dashboard(user=mock_user)

    assert isinstance(dashboard, pn.layout.Columnable)

    found_error_alert = False
    found_empty_dataframe = False
    for item in dashboard:
        if isinstance(item, pn.pane.Alert) and item.alert_type == 'danger':
            found_error_alert = True
            assert "Could not connect to SAP HANA" in item.object
        if isinstance(item, pn.pane.DataFrame): # Should still have a DataFrame pane, but empty
            found_empty_dataframe = True
            assert item.object.empty

    assert found_error_alert, "Dashboard should display a danger alert for connection failure."
    assert found_empty_dataframe, "Dashboard should display an empty DataFrame on connection failure."
    
    app.main.hana_connector.get_hana_connection.assert_called_once()
    # get_sales_data should not be called if connection fails
    app.main.hana_connector.get_sales_data.assert_not_called()


def test_create_sales_dashboard_sales_data_empty(mock_user, mock_hana_connection_success, mocker):
    """
    Test create_sales_dashboard when connection is successful but sales data is empty.
    """
    mocker.patch('app.main.hana_connector.get_sales_data', return_value=pd.DataFrame()) # Empty DF
    
    dashboard = create_sales_dashboard(user=mock_user)

    assert isinstance(dashboard, pn.layout.Columnable)

    found_warning_alert = False
    found_empty_dataframe = False
    for item in dashboard:
        if isinstance(item, pn.pane.Alert) and item.alert_type == 'warning':
            # This could be a specific warning for no data, or a general one
            if "No sales data available" in item.object:
                 found_warning_alert = True
        if isinstance(item, pn.pane.DataFrame):
            found_empty_dataframe = True
            assert item.object.empty

    assert found_warning_alert, "Dashboard should display a warning alert for empty sales data."
    assert found_empty_dataframe, "Dashboard should display an empty DataFrame if sales data is empty."

    app.main.hana_connector.get_hana_connection.assert_called_once()
    app.main.hana_connector.get_sales_data.assert_called_once_with(mock_hana_connection_success)
    mock_hana_connection_success.close.assert_called_once()


def test_create_sales_dashboard_no_user():
    """
    Test create_sales_dashboard when no user is provided.
    """
    dashboard = create_sales_dashboard(user=None)
    assert isinstance(dashboard, pn.pane.Markdown)
    assert "Error: No user context provided." in dashboard.object


def test_create_sales_dashboard_hana_connection_close_exception(mock_user, mock_hana_connection_success, mock_get_sales_data_success, mocker):
    """
    Test that an exception during hana_conn.close() is handled and an alert is shown.
    """
    mock_hana_connection_success.close.side_effect = Exception("Failed to close connection")
    
    dashboard = create_sales_dashboard(user=mock_user)

    assert isinstance(dashboard, pn.layout.Columnable)
    
    found_warning_alert_for_close = False
    for item in dashboard:
        if isinstance(item, pn.pane.Alert) and item.alert_type == 'warning':
            if "Warning: Could not close SAP HANA connection" in item.object:
                found_warning_alert_for_close = True
                assert "Failed to close connection" in item.object # Check if the specific error is mentioned
                
    assert found_warning_alert_for_close, "Dashboard should display a warning alert if closing connection fails."

    app.main.hana_connector.get_hana_connection.assert_called_once()
    app.main.hana_connector.get_sales_data.assert_called_once_with(mock_hana_connection_success)
    mock_hana_connection_success.close.assert_called_once()

# Note: More specific tests could be added to check the exact content or structure
# of the dashboard components if needed, beyond just their types.
# For example, checking titles, specific text in Markdown, etc.
# This set of tests focuses on the main logic paths and component presence.
