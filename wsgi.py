# wsgi.py
"""
Punto de entrada para servidores WSGI (gunicorn, uwsgi).
Uso: gunicorn wsgi:app
"""
from app import app

if __name__ == "__main__":
    app.run()