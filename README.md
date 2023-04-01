# followingapp
An Application where user can upload photos and view photo's uploaded by others

# Dependencies
We need Docker installed in our system to run the application

# Used tools/technologies
* `Python`
* `FastAPI`
* `SQLAlchemy`
* `postgres` with `postgis` extension
* `Jinja Template`
* `Alembic`
* `Docker`

# Installation
To install this application, first clone the repository to your local machine:

```
https://github.com/rafy13/followingapp.git
```
To run this, first nevigate to the project root directory. We need to add a `.env` file in directory `../<root-directory>/.env` of the project and set the all the environment variable there. Here is an example of the `.env` file. Please replace the value for `MAIL_SERVICE_EMAIL` and `MAIL_PASSWORD` with your gmail and a generated app password. Pease follow the [documentation](https://support.google.com/accounts/answer/185833?hl=en) to see how to create app password for a gmail account.

```
DATABASE_URL = postgresql+psycopg2://admin:admin@database:5432/followingappdb

POSTGRES_SERVER = database
POSTGRES_USER = admin
POSTGRES_PASSWORD = admin
POSTGRES_PORT = 5432
POSTGRES_DB = followingappdb
SECRET_KEY = mysupersecurejwtsecretkeyforfollowingapp

MAIL_SERVICE_EMAIL=example@gmail.com
MAIL_PASSWORD=example-app-password
MAIL_PORT=587
MAIL_SERVER="smtp.gmail.com"
MAIL_TLS=True
MAIL_SSL=False
```

Now to run the application, run the command below: 

```
cd <project-root-directory>
docker-compose up
```
This will start the web server on port 8000 by default. You can access the server by visiting http://localhost:8000 in your browser.

# Functionality
## Registration
Navigate to http://localhost:8000/register to sign up. User need to allow access to his location in order to get his latitude and longitude.

After submitting registration form with valid data, an email will be sent to user's email address containing the account activation url. User can activate his account by clicking the activation link. The activation link will automatically expire after 1 day.

## Login
Navigate to http://localhost:8000/login to login. An active user can login providing his valid email address and password.

## Home Page or the Timeline Page
In the timeline Page(http://localhost:8000/) user will see all the photos uploaded by the user's he is following including his uploaded photos. User can Like or Dislike a photo in his timeline

## My profile page
The `My Profile`(http://localhost:8000/users) show details information for currently logged in user. User can `upload profile picture` and `create new gallery`. List of all gallery for the logged in user are also shown in My profile page

## Gallery Page
We can open a Gallery by clicking a gallery name

## Find Users Page
In `Users List`(http://localhost:8000/users) page, all the nearby active user are shown. We can `Follow` or `Unfollow` an user for users List page

## Gallery Page
We can open a `Gallery` by clicking on the name of a gallery. In gallery page, owner of a gallery will be able to upload new image.

## User Detail Page
We can view a User Details by clicking his name. On user details page, a follower of that user will be able to see his galleries.

## Logout
User can logout by clicking the Logout menu from Nav bar

# Quick Testing
We can login with the following user and password into our application in case we face any issue to generate app password for the gmail and activate registered account.
```
email: c@mail.com
Password: 1234567890

email: d@mail.com
Password: 1234567890
```

# Improvement Scope
1. I wasn't able to complete implementation for real time notification for mutual follows
2. Add follow unfollow buttons in user details page
3. Add like dislike functionality on gallery page
4. The UI could be more user friendly
5. More form validator could be implemented in the existing forms
6. Add functionality to update user information
7. Add functionality to resend activation URL
8. Write test cases
9. Use cloud based storage instead of local file storage to store uploaded photos.

# Known Issues
1. Sometimes it fails when running `docker-compose up` command for the very first time. I wasn't able to find the root cause of this yet.
2. We are rendering the whole page if any component is updated on a page
