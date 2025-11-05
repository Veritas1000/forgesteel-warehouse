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
python3 -m pip install -r requirements.txt
```

Update dependencies to latest:
```bash
python -m pip freeze > requirements.txt
```

Run the api backend in development mode:
```bash
flask --app 'forgesteel_warehouse:init_app()' run --debug
```

### Run tests

```bash
python -m pytest .
```

### Build container

```bash
docker build -t fs-warehouse:latest -f Containerfile .
```

### Run container

```bash
docker run --rm -p 5000:5000 --name fs-warehouse fs-warehouse:latest 
```

### Todos

- [x] Initial database
- [x] Direct (api token) Authentication
- [x] Initial container
- [ ] Bootstrap single-user container
- [ ] Secure deployment
- [ ] CI
- [ ] Integration/smoke tests
- [ ] Add actual data storage
- [ ] Add TLS
- [ ] Patreon OAuth integration
