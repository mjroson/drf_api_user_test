### Local deploy:

Dependecias: docker & pre-commit

1. Copy the environment file example and changes as you need.

   `cp dev.env .env`

2. Install githooks using pre-commit
   `pre-commit install`

3. Build and run project

   `docker compose up`

## Utils commands

**Run tests**

`docker compose run --rm django pytest`

**Run test with ouput report of coverage**

`docker compose run --rm django pytest --cov=apps`

**Run test and generate coverage html report**

`docker compose run --rm django pytest --cov=apps --cov-report html -x`

**Generate graph models**
More info: https://django-extensions.readthedocs.io/en/latest/graph_models.html

`docker compose run --rm django python manage.py graph_models -a -g -o models.png`

**Shell plus**
More info: https://django-extensions.readthedocs.io/en/latest/shell_plus.html

`docker compose run --rm django python manage.py shell_plus`

**Django development server plus**
More info: https://django-extensions.readthedocs.io/en/latest/runserver_plus.html

`docker compose run --rm --service-port django python manage.py runserver_plus 0.0.0.0:8000`
