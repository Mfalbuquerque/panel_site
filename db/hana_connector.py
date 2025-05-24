import os
import pandas as pd
from hana_ml.dataframe import ConnectionContext

def get_hana_connection():
    """
    Retrieves SAP HANA connection parameters from environment variables
    and establishes a connection.

    Environment Variables:
        HANA_ADDRESS (str): The address of the SAP HANA instance.
        HANA_PORT (int): The port number for the SAP HANA instance.
        HANA_USER (str): The username for SAP HANA authentication.
        HANA_PASSWORD (str): The password for SAP HANA authentication.

    Returns:
        hana_ml.dataframe.ConnectionContext or None: 
            The connection object if successful, None otherwise.
    """
    address = os.getenv("HANA_ADDRESS")
    port = os.getenv("HANA_PORT")
    user = os.getenv("HANA_USER")
    password = os.getenv("HANA_PASSWORD")

    if not all([address, port, user, password]):
        print("Error: Missing one or more SAP HANA connection environment variables.")
        print("Please set HANA_ADDRESS, HANA_PORT, HANA_USER, and HANA_PASSWORD.")
        return None

    try:
        port = int(port) # Ensure port is an integer
        connection = ConnectionContext(
            address=address,
            port=port,
            user=user,
            password=password
        )
        print("Successfully connected to SAP HANA.")
        return connection
    except ValueError:
        print(f"Error: HANA_PORT ('{port}') is not a valid integer.")
        return None
    except Exception as e:
        print(f"Error connecting to SAP HANA: {e}")
        return None

def get_sales_data(cc: ConnectionContext):
    """
    (Placeholder) Simulates fetching sales data from SAP HANA.

    Args:
        cc (hana_ml.dataframe.ConnectionContext): The SAP HANA connection object.

    Returns:
        pandas.DataFrame: Mock sales data.
    """
    if not cc:
        print("Error: No SAP HANA connection provided to get_sales_data.")
        return pd.DataFrame() # Return empty DataFrame if no connection

    print("Simulating fetching sales data...")
    # In a real scenario, you would use cc.sql() or other hana-ml methods
    # For example:
    # try:
    #     df_sales = cc.sql("SELECT * FROM SALES_TABLE").collect()
    #     return df_sales
    # except Exception as e:
    #     print(f"Error fetching sales data: {e}")
    #     return pd.DataFrame()

    mock_data = {
        'OrderID': [1, 2, 3, 4, 5],
        'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Webcam'],
        'Quantity': [1, 2, 1, 1, 3],
        'Price': [1200, 25, 75, 300, 50]
    }
    return pd.DataFrame(mock_data)

def get_customer_data(cc: ConnectionContext):
    """
    (Placeholder) Simulates fetching customer data from SAP HANA.

    Args:
        cc (hana_ml.dataframe.ConnectionContext): The SAP HANA connection object.

    Returns:
        pandas.DataFrame: Mock customer data.
    """
    if not cc:
        print("Error: No SAP HANA connection provided to get_customer_data.")
        return pd.DataFrame() # Return empty DataFrame if no connection

    print("Simulating fetching customer data...")
    # In a real scenario, you would use cc.sql() or other hana-ml methods
    # For example:
    # try:
    #     df_customers = cc.sql("SELECT * FROM CUSTOMER_TABLE").collect()
    #     return df_customers
    # except Exception as e:
    #     print(f"Error fetching customer data: {e}")
    #     return pd.DataFrame()

    mock_data = {
        'CustomerID': [101, 102, 103, 104, 105],
        'Name': ['Alice Smith', 'Bob Johnson', 'Charlie Brown', 'Diana Prince', 'Edward King'],
        'Segment': ['Retail', 'Wholesale', 'Retail', 'Corporate', 'Retail']
    }
    return pd.DataFrame(mock_data)

if __name__ == '__main__':
    # Example usage (requires environment variables to be set)
    # This part is for testing and won't run when imported as a module.
    print("Attempting to connect to HANA (ensure env vars are set)...")
    # You would need to set these in your environment to test:
    # export HANA_ADDRESS='your_hana_address'
    # export HANA_PORT='your_hana_port'
    # export HANA_USER='your_hana_user'
    # export HANA_PASSWORD='your_hana_password'
    
    conn = get_hana_connection()

    if conn:
        print("\nFetching sales data...")
        sales_df = get_sales_data(conn)
        if not sales_df.empty:
            print("Sales Data:")
            print(sales_df.head())

        print("\nFetching customer data...")
        customer_df = get_customer_data(conn)
        if not customer_df.empty:
            print("Customer Data:")
            print(customer_df.head())
        
        # Close the connection when done
        try:
            conn.close()
            print("\nSAP HANA connection closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")
    else:
        print("\nFailed to connect to SAP HANA. Skipping data fetching examples.")
