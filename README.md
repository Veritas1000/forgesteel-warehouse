# Forge Steel - Vault

A data backend for [Forge Steel](https://andyaiken.github.io/forgesteel/)

## Usage

## Development

### Set up python virtual environment
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
flask --app 'forgesteel_vault:init_app()' run --debug
```

### API layer

- REST api for user authentication and handling data transfers to/from forgesteel.

### Data layer

- postgres database storing jbon documents of raw forgesteel data models

### Todos

- [ ] Initial database
