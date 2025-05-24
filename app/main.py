import panel as pn
import panel.template as pt
import pandas as pd # For creating a placeholder DataFrame if data fetching fails

# Assuming your custom modules are structured as described
from app import auth # Placeholder, not used in this step but good for structure
from db import hana_connector
# from db import models # Placeholder, not used in this step

pn.extension(sizing_mode="stretch_width")

# Placeholder for the current user (replace with actual login logic later)
# For now, we simulate a logged-in user.
class MockUser:
    def __init__(self, username):
        self.username = username

current_user = MockUser(username="testuser")

def create_sales_dashboard(user):
    """
    Generates a sales dashboard for the given user.
    """
    if not user:
        return pn.pane.Markdown("## Error: No user context provided.")

    dashboard_components = []
    # TODO: Security - Ensure username is properly sanitized if it can contain special characters.
    # Panel's Markdown pane might handle HTML escaping, but it's good practice to be aware.
    # If user.username were to come from a source that could inject HTML/JS,
    # it would need explicit sanitization before being rendered in Markdown.
    dashboard_components.append(pn.pane.Markdown(f"# Sales Dashboard for {user.username}"))

    # General XSS Prevention Note:
    # If ever adding custom HTML/JavaScript components or directly rendering user-supplied
    # content into HTML templates (e.g., via Jinja2 without proper autoescaping or manual
    # escaping), ensure that all user-generated content is escaped to prevent XSS attacks.
    # Panel components like pn.pane.DataFrame are generally safe for displaying data.

    # Attempt to get HANA connection
    hana_conn = hana_connector.get_hana_connection()

    if hana_conn is None:
        dashboard_components.append(
            pn.pane.Alert("Error: Could not connect to SAP HANA. Please check connection details or environment variables.", alert_type="danger")
        )
        # Optionally, display an empty DataFrame or a message
        sales_df_pane = pn.pane.DataFrame(pd.DataFrame(), name="Sales Data", width=800, height=300)

    else:
        dashboard_components.append(
            pn.pane.Alert("Successfully connected to SAP HANA.", alert_type="success")
        )
        # Fetch sales data
        sales_df = hana_connector.get_sales_data(hana_conn)
        
        if sales_df.empty:
            dashboard_components.append(
                pn.pane.Alert("No sales data available or an error occurred during fetching.", alert_type="warning")
            )
            sales_df_pane = pn.pane.DataFrame(pd.DataFrame(), name="Sales Data", width=800, height=300)
        else:
            # Create a Panel component to display sales data
            sales_df_pane = pn.pane.DataFrame(sales_df, name="Sales Data", width=800, height=300, show_index=False)
        
        # Close the connection (important!)
        try:
            hana_conn.close()
            print("SAP HANA connection closed.")
        except Exception as e:
            print(f"Error closing SAP HANA connection: {e}")
            dashboard_components.append(
                pn.pane.Alert(f"Warning: Could not close SAP HANA connection: {e}", alert_type="warning")
            )


    dashboard_components.append(sales_df_pane)
    
    # Return a Panel layout
    return pn.Column(*dashboard_components, sizing_mode="stretch_both")

# Create a Panel template
# Using FastListTemplate as an example
template = pt.FastListTemplate(
    title="Sales Dashboard Application",
    # sidebar=["Navigation can go here"], # Example sidebar content
    # header_background="#007bff", # Example header color
)

# For now, directly add the dashboard to the main area assuming a user is logged in
if current_user:
    dashboard_view = create_sales_dashboard(current_user)
    template.main.append(dashboard_view)
else:
    # This part will be replaced by a login screen in a later step
    template.main.append(
        pn.Column(
            pn.pane.Markdown("## Please Log In"),
            # Placeholder for login form
            pn.widgets.TextInput(name="Username", placeholder="Enter your username"),
            pn.widgets.PasswordInput(name="Password", placeholder="Enter your password"),
            pn.widgets.Button(name="Login", button_type="primary")
        )
    )

# Basic serve logic for running as a script
if __name__ == "__main__":
    # This makes the app viewable when running 'python app/main.py'
    # For a more robust deployment, you'd use 'panel serve app/main.py'
    template.show() 

# To make it servable with `panel serve app/main.py`
# template.servable() # Call this if you intend to run `panel serve app/main.py`
# If you use .servable(), typically you don't need .show() in __main__
# For development, .show() is fine. For deployment, .servable() is preferred.
# For this task, let's make it servable for `panel serve`
template.servable()
