# ECOMMERCE STORE (DJANGO REST FRAMEWORK)

![alt text](https://github.com/kayprogrammer/ecommerce-store-drf/blob/main/display/drf.png?raw=true)


#### Django Docs: [Documentation](https://www.django-rest-framework.org/)
#### PG ADMIN: [pgadmin.org](https://www.pgadmin.org) 


## How to run locally

* Download this repo or run: 
```bash
    $ git clone git@github.com:kayprogrammer/ecommerce-store-drf.git
```

#### In the root directory:
- Install all dependencies
```bash
    $ pip install -r requirements.txt
```
- Create an `.env` file and copy the contents from the `.env.example` to the file and set the respective values. A postgres database can be created with PG ADMIN or psql

- Run Locally
```bash
    $ python manage.py migrate
```
```bash
    $ python manage.py runserver
```

- Run With Docker
```bash
    $ docker-compose up --build -d --remove-orphans
```
OR
```bash
    $ make build
```

- Test Coverage
```bash
    $ pytest --disable-warnings -vv
```
OR
```bash
    $ make test
```

## Docs
#### API Url: [E-Store DRF Swagger Docs](https://estore-drf.fly.dev/) 

![alt text](https://github.com/kayprogrammer/ecommerce-store-drf/blob/main/display/disp1.png?raw=true)

![alt text](https://github.com/kayprogrammer/ecommerce-store-drf/blob/main/display/disp2.png?raw=true)

![alt text](https://github.com/kayprogrammer/ecommerce-store-drf/blob/main/display/disp3.png?raw=true)


## ADMIN PAGE [E-Store Admin](https://estore-drf.fly.dev/admin/) 
Check .env.example file for admin credentials

![alt text](https://github.com/kayprogrammer/ecommerce-store-drf/blob/main/display/admin.png?raw=true)