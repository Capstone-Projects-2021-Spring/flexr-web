# Running Django

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

# Creating a View method
1. Define the endpoint in /flexr/flex_web/urls.py
2. If you're making a webpage
    * Create the html page in /flexr/templates/flexr_web/
    * Create the method in the top website section of the /flexr/flex_web/views.py
    * return render(request, "/flexr_web/<the website html page>", {"<name of variable given to html>":<object you would like to pass html>})
3. If you're making an API endpoint
    * Create the method in the appropriate section of the /flexr/flex_web/views.py (it is seperated by database object)
    * return JSONResponse({})
    * more instructions to come once the Class based views are in place



# Project overview

# Contributors
