# Forge Steel - Warehouse

A data backend for [Forge Steel](https://andyaiken.github.io/forgesteel/)

## Usage

## Development

### Set up python virtual environment
Create  the virtual environment:
```bash
python3 -m venv .venv
```

Activate the virtual environment:
```bash
. .venv/bin/activate
```

Install dependencies:
```bash
python -m pip install -r requirements.txt
```

Update dependencies to latest:
```bash
python -m pip freeze > requirements.txt
```

Run the api backend in development mode:
```bash
python wsgi.py
```

### Run tests

```bash
python -m pytest .
```

With coverage:
```bash
python -m pytest --cov --cov-report term --cov-report xml:coverage.xml
```

### Build container

```bash
docker build -t fs-warehouse:latest -f Containerfile .
```

### Run container

```bash
docker run --rm -p 5000:5000 -v <local-dir>:/data --name fs-warehouse fs-warehouse:latest 
```

### Todos

- [x] Initial database
- [x] Direct (api token) Authentication
- [x] Initial container
- [x] Bootstrap single-user container
- [x] Persistent container storage
- [x] Secure deployment
    - [x] JWT_SECRET_KEY
    - [x] SECRET_KEY
- [x] CI setup
- [ ] Unit test and coverage reports in CI
- [ ] Integration/smoke tests
- [ ] pipeline cleanup job
- [ ] Add TLS? Or assume proxy?
- [ ] Add postgres storage support?
- [ ] Rotating/regenerating single-user key
- [ ] Patreon OAuth integration
