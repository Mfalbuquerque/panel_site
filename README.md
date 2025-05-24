# Python Panel Sales Dashboard with SAP HANA Integration

## Overview

This project is a Python-based web application that provides interactive sales dashboards using the [Panel](https://panel.holoviz.org/) framework. It connects to an SAP HANA database to fetch data and includes features for user authentication and session management. The primary goal is to showcase how to build secure, data-driven web applications with Panel.

## Features

*   **User Authentication:** Secure user login and session management (currently uses placeholder DB interactions, with full DB integration planned).
*   **Interactive Dashboards:** Dynamically generated sales dashboards using Panel components.
*   **SAP HANA Integration:** Connects to SAP HANA to fetch data (currently uses mock data, with real queries planned).
*   **Modular Design:** Separated components for application logic, database interaction, and user interface elements.
*   **Security Conscious:** Uses environment variables for sensitive data and includes considerations for web security best practices.
*   **Test Suite:** Unit tests for authentication, database connectors, and dashboard components.

## Project Structure

```
.
├── .env.example        # Example environment variable configuration
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── README.md           # This file
├── app/                # Core application logic
│   ├── __init__.py
│   ├── auth.py         # Authentication functions (user/session management)
│   ├── main.py         # Main Panel application, dashboard definitions
├── db/                 # Database related modules
│   ├── __init__.py
│   ├── hana_connector.py # SAP HANA connection and data fetching logic
│   ├── models.py       # SQLAlchemy models for User and Session
├── requirements-dev.txt # Dependencies for development and testing
├── requirements.txt    # Main application dependencies
├── static/             # Static assets (CSS, JS, images - if any, .gitkeep for now)
│   └── .gitkeep
├── templates/          # HTML templates (if needed by Panel or Flask later, .gitkeep for now)
│   └── .gitkeep
└── tests/              # Automated tests
    ├── __init__.py
    ├── test_auth.py
    ├── test_hana_connector.py
    └── test_main.py
```

*   **`app/`**: Contains the main application logic, including Panel dashboard definitions (`main.py`) and authentication (`auth.py`).
*   **`db/`**: Houses modules for database interactions. This includes the SAP HANA connector (`hana_connector.py`) and SQLAlchemy models (`models.py`) for user and session data.
*   **`static/`**: Intended for static files like CSS, JavaScript, and images. Currently contains a `.gitkeep` file.
*   **`templates/`**: Intended for HTML templates if the application evolves to use server-side HTML rendering (e.g., for a login page). Currently contains a `.gitkeep` file.
*   **`tests/`**: Contains all automated tests for the application.

## Setup and Installation

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)
*   Access to an SAP HANA instance (for full functionality, though mock data is used initially).

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install the main application dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    Install development and testing dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```

4.  **Environment Variables:**
    The application uses environment variables to manage sensitive configuration, such as database credentials and secret keys.
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and provide actual values for the following variables:
        *   `HANA_ADDRESS`: Your SAP HANA instance address.
        *   `HANA_PORT`: Your SAP HANA instance port.
        *   `HANA_USER`: Your SAP HANA username.
        *   `HANA_PASSWORD`: Your SAP HANA password.
        *   `APP_SECRET_KEY`: A strong, unique secret key for session management and other cryptographic operations. You can generate one using Python:
            ```python
            import os
            os.urandom(24).hex()
            ```
    *   **SAP HANA Database Setup:** This project assumes you have an existing SAP HANA database with the necessary tables and permissions for the specified user. The exact DDL for tables is not yet managed by this application (see TODOs). For now, the data fetching functions in `db/hana_connector.py` use mock Pandas DataFrames.

5.  **Database Initialization (Manual/TODO):**
    The SQLAlchemy models `User` and `Session` are defined in `db/models.py`. Currently, table creation is not automated.
    *   **TODO:** Implement a database migration script (e.g., using Alembic) or a simple initialization script to create these tables in your database based on the models.
    *   For now, if you were to connect to a real database for `User` and `Session` storage, you would need to ensure these tables exist. The SAP HANA data for the dashboards themselves is assumed to be in pre-existing tables.

## Running the Application

1.  **Ensure Environment Variables are Set:**
    Make sure your `.env` file is correctly populated and accessible, or that the environment variables are set in your shell session.

2.  **Start the Panel Server:**
    ```bash
    panel serve app/main.py --show --autoreload
    ```
    *   `--show`: Opens the application in your default web browser.
    *   `--autoreload`: Automatically reloads the application when code changes are detected.

3.  **Access in Browser:**
    If it doesn't open automatically, navigate to `http://localhost:5006` (or the port indicated in the console output if 5006 is busy).

## Running Tests

1.  **Ensure Development Dependencies are Installed:**
    If you haven't already, run `pip install -r requirements-dev.txt`.

2.  **Run Pytest:**
    From the root directory of the project:
    ```bash
    pytest
    ```
    This will discover and run all tests in the `tests/` directory.

## Security Notes

*   **Environment Variables:** All sensitive information (database credentials, secret keys) is managed via environment variables and should not be hardcoded or committed to version control. The `.env` file is included in `.gitignore`.
*   **Password Hashing:** User passwords (when fully implemented with DB persistence) are hashed using `bcrypt`.
*   **Session Management:** Secure session IDs are generated using `os.urandom`. Session expiry is implemented.
    *   **TODO:** Implement session regeneration on login to further mitigate session fixation risks.
*   **XSS Prevention:** Panel components like `pn.pane.DataFrame` are generally safe for displaying data. Comments in `app/main.py` remind developers to sanitize user-generated content if it's ever rendered directly into HTML or Markdown that could interpret HTML/JavaScript.
*   **Dependencies:** Regularly update dependencies to patch known vulnerabilities.

## TODO/Future Enhancements

*   **Full Database Integration:**
    *   Implement complete database persistence for `User` and `Session` models using SQLAlchemy, replacing current placeholder logic in `app/auth.py`.
    *   Connect to a real database for user/session storage.
*   **Real SAP HANA Queries:** Replace mock data fetching in `db/hana_connector.py` with actual SQL queries to SAP HANA using `hana-ml`.
*   **Advanced Dashboards:** Develop more complex and interactive dashboards with various Panel widgets and plots.
*   **Login Page UI:** Create a proper HTML form or Panel-based UI for user login instead of relying on placeholder user objects.
*   **Database Migrations:** Implement database schema migrations (e.g., using Alembic or a custom script) to manage changes to the `User` and `Session` table structures.
*   **Error Handling:** Enhance global error handling and user feedback mechanisms.
*   **Logging:** Implement more comprehensive logging throughout the application.
*   **Deployment:** Document steps for deploying to a production-like environment (e.g., using Docker, a reverse proxy like Nginx).

This README provides a good starting point for understanding, setting up, and running the application.
```
