# VibeSocial — Social Media Platform (CodeAlpha Task 2)

A full-stack social media web application built with **Python**, **Django**, **SQLite**, and a **Rich Purple + Neon Pink** glassmorphism UI.

## Features
- User Registration, Login & Logout (`@madiha_dev` demo account / custom sign-up)
- Create & Delete Posts with optional image URL and category tags (`#WebDev`, `#UIUX`, `#CareerTips`, `#General`)
- Like / Unlike toggle and nested Comments on posts
- Follow / Unfollow creators with follower & following counts
- Search posts/users and filter by tags
- Profile viewing & live bio/badge editing

## Tech Stack
- **Backend:** Python, Django, Django ORM
- **Database:** SQLite
- **Frontend:** HTML5, Custom Glassmorphism CSS, Vanilla JavaScript

## Run Locally
```bash
python manage.py makemigrations social
python manage.py migrate
python manage.py runserver