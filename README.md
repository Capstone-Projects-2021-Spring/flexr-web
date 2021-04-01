# Flexr Sync Server
The repository for the Flexr sync server.

## Project overview

The sync server provides data syncing capabilities to the 
web browser as well as a frontend website to modify and
view the data from any browser.

Main repository: [Capstone-Projects-2021-Spring/project-multi-view-mobile-browser](https://github.com/Capstone-Projects-2021-Spring/project-multi-view-mobile-browser)

## Table of Contents
* [Getting Started](#getting-started)
* [Development Notes](#development-notes)
    * [Opening a new terminal](#opening-a-new-terminal)
    * [Things to Remember When Pulling](#things-to-remember-when-pulling)
    * [Adding a dependency](#adding-a-dependency)
    * [Updating Dependencies](#updating-dependencies)
    * [Creating a View method](#creating-a-view-method)
* [Troubleshooting](#troubleshooting)
* [Contributors](#contributors)

## Getting Started

1. Clone the Repository
```shell
git clone https://github.com/Capstone-Projects-2021-Spring/flexr-web.git
```
2. Navigate to the project directory
```shell
cd flexr-web/flexr
```
3. Create a virtual environment
```shell
python3 -m venv env
```
4. Enable the virtual environment 
On Linux/MacOS:
```shell
source env/bin/activate
```

On Windows:
```shell
env\Scripts\activate
```

If this is successful you'll see `(env)` at the 
beginning of the terminal line.

5. Install the requirements
```shell
pip3 install -r requirements.txt
```

6. Setup the database 
```shell
python3 manage.py makemigrations flexr_web
python3 manage.py migrate
```

7. Create a superuser account
```shell
python3 mange.py createsuperuser
```
This will create a user that has access to the 
django admin panel so remember the username and
password you specify for it.

8. Run the server 
```shell
python3 mangae.py runserver
```

9. Open the website in your browser of choice
    * Home Page: http://127.0.0.1:8000/
    * Admin Panel: http://127.0.0.1:8000/admin

Note: This superuser does not have a Flexr 
Account associated with it as the users are 
managed by django itself and the accounts are
managed by Flexr. This means you'll have to go
into the admin panel to add a new account for this
user.

1. Go to: http://127.0.0.1:8000/admin/flexr_web/account/add/
2. Select your user in the dropdown
3. Give the account a username, email, and phone number
4. Change the account type if you would like
5. Scroll down to the bottom of the page and click save


## Development Notes

### Opening a new terminal

When openening a new terminal window you need to always be sure
you activate the virtual environment to be able to have the
dependencies for the project. You can do this by running the
following command.

On Linux/MacOS:
```shell
source env/bin/activate
```

On Windows:
```shell
env\Scripts\activate
```

### Things to Remember When Pulling
If any modifications were made to the models you need to run
```shell
python3 manage.py makemigrations flexr_web
```
and it might ask to fill in a value if a field is added to a model, 
just press 1 and input a value that would make sense.

Ex: 
If the field is supposed to be a URL put `"https://www.example.org/"`

Then run
```shell
python3 manage.py migrate
```
to update your local database.


### Adding a dependency
1. Make sure you are in you virtual environment (check for `(env)`)
2. Install the dependency
```shell
pip3 install <dependency>
```
3. Update the requirements.txt file
```shell
pip3 freeze > requirements.txt
```

### Updating Dependencies
If a dependency has been added by someone else, make sure you run 
the following command to ensure you have the dependency installed.

Note: Make sure you are in you virtual environment (check for `(env)`)
```shell
pip3 install -r requirements.txt
```

### Creating a View method
1. Look to see if there is a class for the method
    * If there isn't: make one
    * If there is add the method to the class
2. Define the endpoint in /flexr/flex_web/urls.py
3. If you're making a webpage
    * Create the html page in /flexr/templates/flexr_web/
    * Create the method in the top website section of the /flexr/flex_web/views.py
    * `return render(request, "/flexr_web/<the website html page>", {"<name of variable given to html>":<object you would like to pass html>})`
4. If you're making an API endpoint
    * Create the method in the appropriate section of the /flexr/flex_web/views.py (it is seperated by database object)
    * `return JSONResponse({})`
    * more instructions to come once the Class based views are in place
5. Creates tests for the views you created

## Troubleshooting
1. Django: OperationalError No Such Table
      * Fix: python manage.py migrate --run-syncdb
2. Failed to build crpytography
      * Fix: pip3 install hiredis
      * In requirements.txt: change cryptography to 3.1.1
      * In requirements.txt: change Twisted to 21.2.0

## Contributors
* Faris Awad - [@faris-niz](https://www.github.com/faris-niz)
* Evan Fiordeliso - [@FiFiTiDo](https://www.github.com/fifitido)
* Jake Gronikowski - [@jacobgronikowski](https://www.github.com/jacobgronikowski)
* Cole Marano - [@maranc](https://www.github.com/maranc)
* Tyler Powell - [@typow21](https://www.github.com/typow21)
* Pushkin Roye - [@AtanuRoye](https://github.com/AtanuRoye)
* Gerald Whitters - [@WhittersGerald](https://www.github.com/WhittersGerald)