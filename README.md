# Backend for the Pingerini App

The backend for the Pingerini application is designed to support a simple organizer-style tool that aids teams in managing their work. Pingerini enables the creation and sharing of tasks and primarily focuses on "pinging" - sending short messages for specific purposes such as informing team members about the completion of a task or the need for additional time to complete it. Besides facilitating communication among users, the application allows for the formation of groups, enabling shared responsibility for various tasks.

The backend is built using [Django](https://www.djangoproject.com) and [Graphene](https://graphene-python.org) technologies. It was developed over three iterations, each introducing new functionalities. Changes in the database can be observed in the `UML` files, and updates to the supported API are documented in `api.txt`. Additionally, there are `scenarios` provided in the scenario folder.

---

Start server:

0. Go to `pingerini_server` directory.

   ```
   > cd pingerini_server
   ```

1. Install dependecies from `reqiremenets.txt` (in your own environment).

   ```
   > python -m venv ./myenv
   > source myenv/bin/activate
   > pip install -r requirements.txt
   ```

2. Migrate and run server based on `manage.py`.

   ```
   > python manage.py migrate
   > python manage.py runserver
   ```

3. Start conversation with server at http://127.0.0.1:8000/graph/ <br>
   based on provided scenarios and api (using GraphiQL). <br>
   (! when using dates use actual dates, for example deadline for the task must be "in the future")

4. At http://127.0.0.1:8000/admin/ (login: admin, password: admin) you can edit database.

---

Actual UML model:

