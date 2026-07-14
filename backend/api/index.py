"""Vercel serverless entry point for the Django backend.

Vercel's @vercel/python runtime serves the WSGI callable exported as `app`.
The same `config.wsgi` application is used locally under gunicorn.
"""
from config.wsgi import application as app  # noqa: F401
