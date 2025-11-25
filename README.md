# Forge Steel - Warehouse

A data backend for [Forge Steel](https://andyaiken.github.io/forgesteel/)

Forge Steel Warehouse runs as a container that exposes an api which Forge Steel can use to store your Hero and Sourcebook data *outside* your browser. This means you can share data cross devices, and not worry about a browser update wiping out all of your created characters.

## Usage

These instructions assume a familiarity with docker and the linux command-line.

For wider access to your self-hosted forgesteel-warehouse instance, it is also assumed that you have an understanding of things such as port forwarding and/or proxies, firewall security, etc.

### Prerequisites
- `docker` installed and working
    - `podman` should also work fine, just substitute the relevant command name. But if you're using podman, you almost certainly already know this, so why am I even still writing this?
- *(Optional)* Reverse proxy with SSL setup and configured
- *(Optional)* Routed and secured port access to where the container is running.

### Initial setup and configuration
Create a directory on the host machine where the forgesteel-warehouse data and configuration will live. For simplicity, this example will just use a local directory `/data/forgesteel`.

Run fs-warehouse interactively like so:

```bash
run --rm -it --name fs-warehouse -p 5000:5000 -v /data/forgesteel:/data fs-warehouse
```

The first time it starts up, it will initialize the database and generate an API key for you, displaying it in the session - **save it someplace secure**! This is how you will connect Forge Steel with your individual warehouse.

## Development

### Set up python virtual environment
Create  the virtual environment:
```bash
python -m venv .venv
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
python dev_server.py
```

### Run tests
Also install testing dependencies:
```bash
python -m pip install -r requirements-testing.txt
```

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
- [x] Publish to GitHub
- [x] Add actual forgesteel data storage
    - [x] heroes
    - [x] homebrew-settings
    - [x] hidden-setting-ids
    - [x] session
- [ ] Add container publish to CI
- [ ] Integration/smoke tests
    - [ ] verify loading config
    - [ ] bootstrap doesn't overwrite config values
- [ ] pipeline cleanup job
- [ ] Add TLS? Or assume proxy?
- [ ] Add postgres storage support?
- [ ] Rotating/regenerating single-user key
- [ ] Patreon OAuth integration
