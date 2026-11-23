# finalproplan

## Project description
The Community Library Book Tracker is a web application designed to help neighborhood libraries, school clubs, teachers,  organize and manage shared book collections. It addresses common problems such as misplaced books, forgotten return dates, and disorganized lending records by providing a centralized  platform.

## Planned Technology Stack
* **Frontend:** HTML, CSS, and JavaScript 
* **Backend:**  Python Flask 
* **Database:** SQLite
* **Deployment / Tools:**  Docker,Google Cloud Platform 

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Set `FLASK_SECRET_KEY` to a long, random value so sessions remain secure.
4. Start the app with `python app.py`, then open `http://localhost:5000`.

The signup page validates email addresses on the server, requires a password of
at least eight characters, and stores only a password hash. Successful signup
shows a confirmation and redirects to the main application. User records are
stored in `instance/users.sqlite` by default; set `DATABASE_PATH` to use another
database file. The Docker image serves the app with Gunicorn on port 5000.

Run the auth tests with `python -m unittest discover -s tests`.


## Status
Basic function the MVP are set with AI helping fix errors,add suggestions,and help generate code