python manage.py collectstatic --no-input \
&& python manage.py migrate --noinput \
&& gunicorn bdmanga.wsgi --bind 0.0.0.0:8001