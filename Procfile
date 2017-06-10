web: gunicorn wsgi:app   --preload --workers 1 --log-file=- 

init: python db.py
rq-worker: python worker.py
article-scraper: python watch.py