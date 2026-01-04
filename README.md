# Run Together: Manage Club and Races in one place

## Project Overview



## Technical Stack

- Backend Framework: Django 6.0
- Frontend: Django Templates with HTMX (tailwing & DaisyUI)
- State Management:
  - Server-side: Django session
  - Client-side: localStorage for runtogether state persistence
- Database: PostgreSQL with POSTGIS (Production)
- Deployment Stack: Docker

## Development

1. Setup `runtogether/.env` from `runtogether/.env.dist`
1. Install the venv with `uv sync`
1. Create database
   ```
   uv run python manage.py migrate
   ```
1. setup a superuser to be able to manage steps & tasks templates
   ```
   uv run python manage.py createsuperuser
   ```
1. Start the app
   ```
   uv run python manage.py tailwind start
   uv run python manage.py runserver
   ```
1. Open `localhost`, Register an account or login with the superadmin account (not recommended in Production obviously)

## Testing

1. Go to `runtogether` folder
   ```
   cd runtogether
   ```
1. run tests with coverage
   ```
   uv run pytest
   ```

> Pytest options are set in `pyproject.toml`

## Deployment

1. Refer to `docker-compose.yaml`. It is highly not recommended to use a database in Production in the docker-compose.

2. To create a superuser run the following command:

```
docker exec -it <containerid> python3 manage.py createsuperuser
```

> The image is not compatible with a `DEBUG=on` as several dependancies are not installed

> Refer to [this link](https://hub.docker.com/r/coni57/project-runtogether) for images
