#!/bin/bash

# Script de configuracion para API de Mantenimiento de Equipos

echo "Configurando entorno virtual..."
python -m venv venv
source venv/bin/activate

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Ejecutando migraciones..."
python manage.py migrate

echo "Creando superusuario..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com

echo "Configuracion completa. Ejecutar 'python manage.py runserver' para iniciar el servidor."
