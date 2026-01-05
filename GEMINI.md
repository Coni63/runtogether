# Gemini Code Assistant Context

This document provides context for the Gemini Code Assistant to understand the "Run Together" project.

## Project Overview

"Run Together" is a web application designed to manage running clubs and races. It allows users to find, join, and manage club activities and race events.

**Key Technologies:**

*   **Backend:**
    *   Python 3.12+
    *   Django 6.0
    *   PostgreSQL with PostGIS for geospatial data.
*   **Frontend:**
    *   Django Templates
    *   HTMX for dynamic UI updates.
    *   Tailwind CSS for styling.
    *   DaisyUI component library.
*   **Deployment:**
    *   Docker and Docker Compose.
    *   `gunicorn` as the WSGI server.
    *   `nginx` as a reverse proxy and for serving static files.
*   **Dependency Management:**
    *   `uv` for Python packages (see `pyproject.toml`).
    *   `npm` for frontend packages (see `runtogether/theme/static_src/package.json`).

**Project Structure:**

The project is a standard Django project with a multi-app architecture.

*   `runtogether/`: The main Django project directory.
    *   `runtogether/settings.py`: Main settings file.
    *   `runtogether/urls.py`: Root URL configuration.
*   `accounts/`, `city/`, `club/`, `race/`, `home/`, `core/`, `common/`: Individual Django apps, each responsible for a specific domain of the application.
*   `templates/`: Global HTML templates.
*   `static/`: Global static files.
*   `theme/`: The Django app responsible for the frontend theme, containing `static_src` for Tailwind CSS source files.
*   `docker-compose.yaml`: Defines the services for development and production.
*   `.github/workflows/`: Contains CI/CD workflows, including the test suite.

## Building and Running

### Local Development

1.  **Set up environment:** Create a `.env` file in the `runtogether/` directory from the `.env.dist` template.
2.  **Install dependencies:** Use `uv` to install Python dependencies.
    ```shell
    uv sync --all-groups
    ```
3.  **Frontend dependencies:** Navigate to `runtogether/theme/static_src` and run:
    ```shell
    npm install
    ```
4.  **Database migration:**
    ```shell
    uv run python manage.py migrate
    ```
5.  **Create a superuser (optional):**
    ```shell
    uv run python manage.py createsuperuser
    ```
6.  **Run the development servers:**
    ```shell
    # In one terminal, run the Tailwind CSS watcher
    uv run python manage.py tailwind start

    # In a second terminal, run the Django development server
    uv run python manage.py runserver
    ```

### Running with Docker

The project can be run using Docker Compose:

```shell
docker-compose up
```

Refer to `docker-compose.yaml` for service details. The production image is `coni57/runtogether:latest`.

## Testing

The project uses `pytest` for testing.

*   **Run tests locally:**
    ```shell
    cd runtogether
    uv run pytest
    ```
*   **CI:** Tests are automatically run on pull requests to the `master` branch, as defined in `.github/workflows/tests.yml`.

## Development Conventions

*   **Code Style:** The project uses `ruff` for linting and formatting. The configuration is in `pyproject.toml`.
*   **Database:** The application uses PostgreSQL with PostGIS. All database interactions should be done through the Django ORM.
*   **Frontend:** UI is built with Django templates and progressively enhanced with HTMX. Styling is done with Tailwind CSS.
*   **Environment Variables:** Application configuration is managed through environment variables using `django-environ`. A `.env` file is used for local development.
*   **CI/CD:** GitHub Actions are used for continuous integration.
