python manage.py collectstatic --noinput --clear \
&& python manage.py migrate --noinput \
&& gunicorn bdmanga.wsgi --bind 0.0.0.0:8001