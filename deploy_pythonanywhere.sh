#!/bin/bash
cd /home/usuario/repositorio
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch /var/www/usuario_pythonanywhere_com_wsgi.py
