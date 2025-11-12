# Forge Steel - Warehouse

A data backend for [Forge Steel](https://andyaiken.github.io/forgesteel/)

Forge Steel Warehouse runs as a container that exposes an api which Forge Steel can use to store your Hero and Sourcebook data *outside* your browser. This means you can share data cross devices, and not worry about a browser update wiping out all of your created characters.

## Usage

Run fs-warehouse interactively like so:

```bash
run --rm -it --name fs-warehouse -p 5000:5000 -v <local/data>:/data fs-warehouse
```

The first time it starts up, it will initialize the database and generate an API key for you - **save it someplaec secure**! This is how you will connect Forge Steel with your individual warehouse.

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
python -m pytest --cov --cov-report term
```

### Build container

```bash
docker build -t fs-warehouse -f Containerfile .
```

### Run container

```bash
docker run --rm -p 5000:5000 -v <local-dir>:/data --name fs-warehouse fs-warehouse:latest 
```

### Todos

- [x] CI setup
- [x] Unit test and coverage reports in CI
- [ ] Add actual forgesteel data storage
    - [ ] heroes
    - [ ] playbook
    - [ ] homebrew-settings
    - [ ] hidden-setting-ids (?)
    - [ ] session (?)
- [ ] Publish to public (GitHub?)*
- [ ] Integration/smoke tests
    - [ ] verify loading config
    - [ ] bootstrap doesn't overwrite config values
- [ ] pipeline cleanup job
- [ ] Add TLS? Or assume proxy?
- [ ] Add postgres storage support?
- [ ] Rotating/regenerating single-user key
- [ ] Patreon OAuth integration
