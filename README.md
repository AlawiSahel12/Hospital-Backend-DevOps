🚀 Medical Center API (Django Backend)

This is the Django backend API for the Medical Center application. We are using Docker for containerization and Test-Driven Development (TDD).

---

🎬 Start the Application (run commands)

⭐️ `docker-compose build`

🔹 When to use it:

✅ Run it when you change the Dockerfile or dependencies (e.g., requirements.txt).

✅ Before starting the project for the first time.

⭐️ `docker-compose up`

🔹 When to use it:

✅ Run it every time you want to start the application.

⭐️ `docker-compose down`

🔹 When to use it:

✅ When you want to fully stop and remove the containers.

✅ If you need a fresh restart of the project.

---

👀 Development Approach: TDD

We are following Test-Driven Development (TDD).

🧪 Test command:

`docker-compose run --rm app sh -c "python manage.py test"` # run all tests

---

🖥 Running Commands Inside the Docker Container

Since we are using Docker to containerize our Django project and Postgress DB,
you need to run commands inside the container, not directly on your local machine terminal.

To do this, use the following structure:

`docker-compose run --rm app sh -c "your_command_here"`

🔹 Example: To check code formatting with flake8, run:

`docker-compose run --rm app sh -c "flake8"`

---

‼️ Before you push your code to GitHub, make sure to follow these steps:

- Run tests: `docker-compose run --rm app sh -c "python manage.py test"`
- Run code formatter: `docker-compose run --rm app sh -c "flake8"`
- Run the imports ordring `docker-compose run --rm app sh -c "isort ."`

- After you have pushed your code to GitHub, the github actions will run automatically and check two things:
  - The code formatting: it will ensure that your code follows our formatting guidelines.
  - The tests: it will run all tests and ensure they pass.
  - If either of these checks fail, an email will be sent and you should fix the issues and push again.
- If both checks pass, the code will be automatically deployed to the production server.

---

🍀 Linting and errors

- you can use this comment to till flake8 and pylint to ignore this erorr `#noqa`

---

# Generating graphs for the Models

`docker-compose run --rm app sh -c "python manage.py graph_models -a -g > full_models.dot"`

Then go to this websit: https://dreampuf.github.io/GraphvizOnline/?engine=dot

then past the code generated in the .dot file to create the ER disgram for the Models

---

# Pgadmin website to interact with the DB

go to `https://127.0.0.1:5050/`

Login-info in in the docker-compose file and Accounts section

---

# Accounts

Superuser account for Django admin:
Email: dev@example.com
password: dev123456

Real user in the system:
{
"email": "dev@example.com",
"password": "devtestuser1234",
"name": "dev"
}

Account for pgadmin:
admin@example.com
admin123

---

Common commands to be used:
`docker-compose run --rm app sh -c "python manage.py makemigrations"  `
`docker-compose run --rm app sh -c "python manage.py makemigrations"  `

`docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"  `

`docker-compose run --rm app sh -c "python manage.py startapp xxxx"`

`docker-compose run --rm app sh -c "python manage.py  createsuperuser"`

`docker-compose build`

`docker-compose up`

`docker-compose down`

`docker-compose run --rm app sh -c "python manage.py test"`

`docker-compose run --rm app sh -c "flake8"`

`docker-compose run --rm app sh -c "isort ."`

---

Migration problem solution:

1- use the custom script to delete all migrations files:
`python3 scripts/delete_migrations.py`

2- delete the database volume from the docker app

3- create the migrations again:
`docker-compose run --rm app sh -c "python manage.py makemigrations"`

4- migrate the database (using docker-compose up ) or by the command:
`docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"`
5- create the superuser account:
`docker-compose run --rm app sh -c "python manage.py createsuperuser"`
