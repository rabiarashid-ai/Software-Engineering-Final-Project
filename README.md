# Student Course Enrollment System (Django + SQLite)

Simple course enrollment system built with Django and SQLite.

## Quick Start (local)

```bash
cd /Users/mac/software-engineering-project/course_enrollment_django_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000 --noreload
```

Visit `http://127.0.0.1:8000/`.

## Accounts

- Default seeded accounts (added by migrations):
  - Student: `stu` / `st12345678`
  - Admin (staff): `adm` / `ad12345678`
- You can also create accounts via `/signup`. Choose **Student** (enroll/drop courses) or **Admin** (add/edit/delete courses). No superuser required.
- Password rules are relaxed; only matching passwords are required.
- To create a superuser (optional): `python manage.py createsuperuser`

## Data

- 15 sample courses are seeded automatically via migrations (see course list after signup/login).
- Data persists in `db.sqlite3`; keep this file to retain users/enrollments/courses.

## Tests

Run tests (use Python 3.11/3.12 for best compatibility with Django 4.2):
```bash
python manage.py test enrollment
```
