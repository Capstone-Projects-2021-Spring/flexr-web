# Running Django with macOS

1. git clone
2. cd flexr-web
3. python3 -m venv env
4. source env/bin/activate
5. pip3 install django
6. pip3 install Pillow
(TODO need to make a requirements.txt and .gitignore)
8. cd flexr
9. python3 manage.py makemigrations flexr_web
10. python3 manage.py migrate
11. python3 mange.py createsuperuser
12. python3 mangae.py runserver
13. go to http://127.0.0.1:8000/ to go to home page
14. go to http://127.0.0.1:8000/admin to go to the django admin pannel


# Steps to pull
1. pull from dev branch
2. branch off with new feature branch
3. run pip3 install -r requirements.txt
4. If you make changes to requirements run pip3 freeze >> requirements.txt
5. python3 manage.py makemigrations
6. python3 manage.py migrate

# Creating a View method
1. Look to see if there is a class for the method
2. If there isn't, make one
3. If there is add the method to the class
4. Define the endpoint in /flexr/flex_web/urls.py
5. If you're making a webpage
    * Create the html page in /flexr/templates/flexr_web/
    * Create the method in the top website section of the /flexr/flex_web/views.py
    * return render(request, "/flexr_web/<the website html page>", {"<name of variable given to html>":<object you would like to pass html>})
6. If you're making an API endpoint
    * Create the method in the appropriate section of the /flexr/flex_web/views.py (it is seperated by database object)
    * return JSONResponse({})
    * more instructions to come once the Class based views are in place
7. Test!!!



# Project overview

# Contributors

# Troubleshooting
1. Django: OperationalError No Such Table
      * Fix: python manage.py migrate --run-syncdb
