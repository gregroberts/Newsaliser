web: gunicorn wsgi:app   --preload --workers 1 --log-file=- 
init: python db.py
worker: rqworker