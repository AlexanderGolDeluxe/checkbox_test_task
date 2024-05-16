# Project checkbox_test_task
 REST API for creating and viewing invoices with user registration and authorization.
 Developed on the [FastAPI](https://fastapi.tiangolo.com/) framework.  
 Test task for the [Checkbox.ua](https://checkbox.ua)

![Static Badge](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=blue&labelColor=white)
![Static Badge](https://img.shields.io/badge/FastAPI-0.111.0-009485?logo=fastapi&labelColor=white)
![Static Badge](https://img.shields.io/badge/PostgreSQL-white?logo=postgresql)
![Static Badge](https://img.shields.io/badge/PyTest-8.2.0-009FE3?logo=pytest&labelColor=white)

## Installation

### Clone repository
```console
git clone https://github.com/AlexanderGolDeluxe/checkbox_test_task
```

### Make a virtual environment with requirements

```console
pip install -r requirements.txt
```

### Generate RSA private key + public key pair

Generate an RSA private key, of size 2048
```shell
openssl genrsa -out certs/jwt-private.pem 2048
```

Extract the public key from the key pair, which can be used in a certificate
```shell
openssl rsa -in certs/jwt-private.pem -outform PEM -pubout -out certs/jwt-public.pem
```

### Manage environment variables

Rename file [`.env.dist`](/.env.dist) to `.env`
```console
mv .env.dist .env
```

#### Change variables according to your required parameters

Set your PostgreSQL database variables
```
…
### POSTGRESQL SETTINGS ###
PG_USER = "postgres"
PG_PASSWORD = "********"
PG_HOST = "localhost"
PG_PORT = 5432
…
```

> <span style="color:yellow; text-transform: uppercase">***Warning***</span>  
*If you don't want to use PostgreSQL database, just leave `PG_DB_URL` variable empty. SQLite will be used instead*
```
…
PG_DB_URL = ""
…
```

## Launch

```console
uvicorn app:create_app --reload
```

## Testing

For settings, use file [`pyproject.toml`](/pyproject.toml)
```console
pytest -v tests/
```
