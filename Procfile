web: gunicorn company_details.wsgi --log-file -
worker: celery -A company_details worker --loglevel=info --pool=solo
