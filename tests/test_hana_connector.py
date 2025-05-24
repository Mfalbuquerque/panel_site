import pytest
import os
from unittest.mock import patch, MagicMock
import pandas as pd

# Functions to test
from db.hana_connector import (
    get_hana_connection,
    get_sales_data,
    get_customer_data
)

# Mock the ConnectionContext from hana_ml.dataframe if it's not available or for isolation
# If hana_ml is part of requirements-dev.txt or always available, direct import is fine.
# For this example, let's assume we might want to mock it.
try:
    from hana_ml.dataframe import ConnectionContext
except ImportError:
    # Create a mock class if hana_ml is not installed in the test environment
    ConnectionContext = MagicMock()


# --- Tests for get_hana_connection ---

@pytest.fixture
def mock_env_vars(mocker):
    """Fixture to mock environment variables for HANA connection."""
    env_vars = {
        "HANA_ADDRESS": "testhost",
        "HANA_PORT": "30015",
        "HANA_USER": "testuser",
        "HANA_PASSWORD": "testpassword"
    }
    mocker.patch.dict(os.environ, env_vars)
    return env_vars

def test_get_hana_connection_success(mocker, mock_env_vars):
    """Test successful HANA connection when all env vars are set."""
    mock_conn_context_instance = MagicMock(spec=ConnectionContext)
    mock_conn_context_instance.connection = MagicMock() # Mock the actual DB connection if accessed

    # Patch the ConnectionContext constructor
    mocker.patch('db.hana_connector.ConnectionContext', return_value=mock_conn_context_instance)
    
    conn = get_hana_connection()
    
    db.hana_connector.ConnectionContext.assert_called_once_with(
        address="testhost",
        port=30015, # Ensure it's an int
        user="testuser",
        password="testpassword"
    )
    assert conn == mock_conn_context_instance
    # Check if print was called with success message (optional)
    # mocker.patch('builtins.print')
    # builtins.print.assert_any_call("Successfully connected to SAP HANA.")


def test_get_hana_connection_missing_env_vars(mocker, capsys):
    """Test graceful failure when some environment variables are missing."""
    # Ensure at least one variable is missing
    mocker.patch.dict(os.environ, {"HANA_ADDRESS": "onlyone"}) 
    
    conn = get_hana_connection()
    
    assert conn is None
    captured = capsys.readouterr()
    assert "Error: Missing one or more SAP HANA connection environment variables." in captured.out

def test_get_hana_connection_invalid_port(mocker, capsys):
    """Test graceful failure when HANA_PORT is not a valid integer."""
    env_vars = {
        "HANA_ADDRESS": "testhost",
        "HANA_PORT": "notanint", # Invalid port
        "HANA_USER": "testuser",
        "HANA_PASSWORD": "testpassword"
    }
    mocker.patch.dict(os.environ, env_vars)
    
    conn = get_hana_connection()
    
    assert conn is None
    captured = capsys.readouterr()
    assert "Error: HANA_PORT ('notanint') is not a valid integer." in captured.out


def test_get_hana_connection_connection_error(mocker, mock_env_vars, capsys):
    """Test handling of exceptions during ConnectionContext creation."""
    # Mock ConnectionContext to raise an exception
    mocker.patch('db.hana_connector.ConnectionContext', side_effect=Exception("Test connection error"))
    
    conn = get_hana_connection()
    
    assert conn is None
    captured = capsys.readouterr()
    assert "Error connecting to SAP HANA: Test connection error" in captured.out

# --- Tests for data fetching functions ---

@pytest.fixture
def mock_hana_cc():
    """Fixture for a mock SAP HANA ConnectionContext object."""
    cc = MagicMock(spec=ConnectionContext)
    return cc

def test_get_sales_data_success(mock_hana_cc):
    """Test fetching sales data (currently mock implementation)."""
    # The current implementation of get_sales_data returns a static Pandas DataFrame.
    # If it were to use cc.sql(...).collect(), we would mock those calls.
    # For example:
    # mock_df = pd.DataFrame({'col1': [1,2], 'col2': ['a','b']})
    # mock_hana_cc.sql.return_value.collect.return_value = mock_df
    
    sales_df = get_sales_data(mock_hana_cc)
    
    assert isinstance(sales_df, pd.DataFrame)
    assert not sales_df.empty
    # Check for expected columns from the mock data
    expected_cols = ['OrderID', 'Product', 'Quantity', 'Price']
    assert all(col in sales_df.columns for col in expected_cols)

def test_get_sales_data_no_connection(capsys):
    """Test get_sales_data when no connection context is provided."""
    sales_df = get_sales_data(None)
    assert sales_df.empty
    captured = capsys.readouterr()
    assert "Error: No SAP HANA connection provided to get_sales_data." in captured.out


def test_get_customer_data_success(mock_hana_cc):
    """Test fetching customer data (currently mock implementation)."""
    # Similar to get_sales_data, this tests the current mock implementation.
    # mock_df = pd.DataFrame({'id': [101, 102], 'name': ['CustA', 'CustB']})
    # mock_hana_cc.sql.return_value.collect.return_value = mock_df

    customer_df = get_customer_data(mock_hana_cc)
    
    assert isinstance(customer_df, pd.DataFrame)
    assert not customer_df.empty
    # Check for expected columns from the mock data
    expected_cols = ['CustomerID', 'Name', 'Segment']
    assert all(col in customer_df.columns for col in expected_cols)

def test_get_customer_data_no_connection(capsys):
    """Test get_customer_data when no connection context is provided."""
    customer_df = get_customer_data(None)
    assert customer_df.empty
    captured = capsys.readouterr()
    assert "Error: No SAP HANA connection provided to get_customer_data." in captured.out

# If the actual data fetching logic (e.g., cc.sql()) were implemented,
# more detailed mocking would be needed for those specific calls:
#
# def test_get_actual_sales_data_query_error(mocker, mock_hana_cc, capsys):
#     """Example test if actual SQL query was made and failed."""
#     mocker.patch.object(mock_hana_cc, 'sql', side_effect=Exception("SQL Query Failed"))
#     
#     sales_df = get_sales_data(mock_hana_cc) # Assuming get_sales_data calls cc.sql()
#     
#     assert sales_df.empty
#     captured = capsys.readouterr()
#     assert "Error fetching sales data: SQL Query Failed" in captured.out # Or similar error message
#
# This would apply if the placeholder comments in hana_connector.py were replaced with real queries.
