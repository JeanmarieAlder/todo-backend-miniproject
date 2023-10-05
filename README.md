# todobackend-aiohttp

Yet another [todo backend](http://todobackend.com) written in Python 3.5 with aiohttp. Original code [from alec.thoughts import \*](http://justanr.github.io/getting-start-with-aiohttpweb-a-todo-tutorial).

Modified by Jean-Marie Alder for the todo-tag backend miniproject.

## Usage
- Please note that if "python" is not recognized by your machine, try other aliases, like py, python3. Make sure that Python is installed on your system.

- Copy "example.env" to ".env" at the root of the project and adapt if needed. Default values will do for a local environment (localhost:8080).
- Create a virtual environment: ```python -m venv venv``` (or similar, e.g., ```python3 -m venv venv```). 
- Enter the virtual environment: 
  - Mac and Linux: ```source ./venv/bin/activate```
  - Windows: ```.\venv\Scripts\activate.bat``` or ```.\venv\Scripts\Activate.ps1``` for Powershell.
- Inside virtual environment, install all dependencies: ```pip install -r requirements.txt```.
- Once all requirements are installed, run the application using: 
```
python3 run.py
```
- To stop the local server, use ctrl+c
- Finally, read carefully next section to know more about database. Normally, it should be plug and play and no more action is required (unless configurations in .env have been modified)


## Database informations

This project uses SQLite to persist data.
Default database location is at the root of the project and is called "todo.db".

An sql scrit called "create_todo_db.sql" is available to recreate the database if needed. Have a look at this file if you want to know more about default tables and data.

An other database called "backup_todo.db" is a copy of the initial state of the db. It was used during development to ease db rollback and can be used if needed.


## Tests

You can run validate the application with http://www.todobackend.com/specs/.

**Important**: use Firefox to validate the application.
