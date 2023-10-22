# Airport API✈️
#### Django REST framework

The Airport API Service is a versatile backend solution for managing airport-related data and facilitating flight bookings. It offers CRUD (Create, Read, Update, Delete) operations for cities, routes, airplanes, and flights for administrators while providing the opportunity for everyone to book seats for flights through orders.

## Installation

Python3 must be already installed.
Also install PostgreSQL and create db.

```shell
git clone https://github.com/innyshka/airport-API.git
cd airport_api
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
#create .env file based on env.sample
python manage.py migrate
python manage.py runserver #starts Django server
```

## Run with Docker

[Docker](https://www.docker.com/products/docker-desktop) should be installed.
```shell
docker-compose up --build
```

## Accessing the Application

You can now access the API by opening your web browser 
and navigating to http://localhost:8000.

#### Test admin user
```shell
email: admin@admin.com
password: admin
```
- create user api/user/register
- get access token api/user/token
- refresh token api/user/token/refresh
- verify token api/user/token/verify
- your profile api/user/me

#### Available urls
- api/airport/airplane_types/
- api/airport/positions/
- api/airport/crews/
- api/airport/airplanes/
- api/airport/countries/
- api/airport/cities/
- api/airport/airports/
- api/airport/routes/
- api/airport/flights/
- api/airport/orders/

#### Documentation
- api/doc/swagger/
- api/doc/redoc/
- api/schema


## Features
- JWT Authenticated
- Documentation is located in /api/doc/swagger/
- Managing orders and tickets
- CRUD for all entity except User
- filtering with django_filters and query_params
- you can upload image for airplane, crew and airport in api/airport/<entity>/upload-image

## DB structure
![DB structure](drf%20project.drawio.png)
