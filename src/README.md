# Projekt serwisu "Projekty Kół Naukowych"
Serwis ma służyć do obsługi zgłoszeń projetków studentów będących członkami kół naukowych


To setup and run your server:

Install requirements:
  - python -m pip install -r requirements.txt

Run migrations:
  - python manage.py makemigrations
  - python manage.py migrate
  - If the first command doesn't make migrations for all the apps run migrations for each app individually:
    - python manage.py makemigrations 'appname'
    - python manage.py migrate 'appname'
    
    where 'appname' is the name of the app. You get list of your apps by running python manage.py migrate.

Load fixtures to database:
  - python manage.py loaddata announcement grades groups notificationperiod studentclubs
 
Run server:
  - python manage.py runserver
