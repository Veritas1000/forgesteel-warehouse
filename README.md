# Forge Steel - Warehouse

A data backend for [Forge Steel](https://andyaiken.github.io/forgesteel/)

Forge Steel Warehouse runs as a container that exposes an api which Forge Steel can use to store your Hero and Sourcebook data *outside* your browser. This means you can share data cross devices, and not worry about a browser update wiping out all of your created characters.

## Usage

These instructions assume a familiarity with docker and the linux command-line.

For wider access to your self-hosted forgesteel-warehouse instance, it is also assumed that you have an understanding of things such as port forwarding and/or proxies, firewall security, etc.

### Prerequisites
- `docker` installed and working
    - `podman` should also work fine, just substitute the relevant command name. But if you're using podman, you almost certainly already know this, so why am I even still writing?
- *(Optional but HIGHLY recommended)* Reverse proxy with SSL setup and configured
- *(Optional - required for remote access)* Routed and secured port access to where the container is running.

### Initial setup and configuration

Pull the latest image from docker hub:
```bash
docker pull veritas1000/forgesteel-warehouse
```

Create a directory on the host machine where the forgesteel-warehouse data and configuration will live. For simplicity, this example will just use the directory `/data/forgesteel`.

The first time you run forgesteel-warehouse, run it interactively like so:

```bash
run --rm -it --name fs-warehouse -p 5000:5000 -v /data/forgesteel:/data veritas1000/forgesteel-warehouse
```

The first time it starts up, it will initialize the database and generate an API key for you, displaying it in the session - **save it someplace secure**! This is how you will connect Forge Steel with your individual warehouse.

### Running with `docker compose`
You can also create a `compose.yaml` file to run forgesteel-warehouse, a basic compose file might look like this:
```yaml
---
services:
  fs-warehouse:
    image: veritas1000/forgesteel-warehouse:latest
    container_name: fs-warehouse
    volumes:
      - ./instance:/data
    ports:
      - 5000:5000
    restart: unless-stopped
```

This will run the service on port `5000`, with the data stored in the `instance` directory under the current dir (this happens to be the default dir that the dev server uses). If you don't change this volume mount, just make sure that `instance` directory exists.

Then, start forgesteel-warehouse by running `docker compose up -d`

### Connecting with Forge Steel
*Note: This is currently in a closed beta, so you will need to enable the feature flag to see the connection settings for forgesteel-warehouse*

- In Forge Steel, go to the **Admin** section under **Settings**.

- There, expand the 'Forge Steel Warehouse' section, and turn on `Connect with Forge Steel Warehouse'.

- Enter the hostname and port for your warehouse instance (if running locally with the dev server or example compose file above, it will be `http://localhost:5000`)

- Enter the API key displayed when you ran the warehouse the very first time.
![Forge Steel Warehouse settings](docs/images/connection_settings.png)

- At this point, clicking 'Test Connection' should show 'Success!'. You can then save the settings and **refresh Forge Steel** to have it use the warehouse for data storage.

#### Transferring data into the warehouse
Right now, there is no automatic data migration from the old local Forge Steel storage to the Warehouse, so on loading Forge Steel while connected to the Warehouse, it will look like all of your data is gone! However, your local data is still there.

To transfer data into the warehouse:
- Turn off the forgesteel-warehouse connection in the settings.
- Reload Forge Steel in your browser
- Go to [the Forge Steel backup page](https://andyaiken.github.io/forgesteel/#/backup) and download everything you want to bring over to the warehouse.
- Turn back on the forgesteel-warehouse data connection.
- Reload Forge Steel in your browser
- Import everything you exported above back into Forge Steel.
- That data is now stored in your local warehouse!

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

Run the api backend in development mode:
```bash
python dev_server.py
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

### DB migrations



### Dependency upgrade

- Update python dependencies
```bash
pip install --upgrade -r requirements.txt
```
- run tests, verify, etc
- freeze deps
```bash
python -m pip freeze > requirements.txt
```

### Version bump

- update `__version__.py` with new version
- commit
- tag commit
```bash
git tag vX.Y.Z
```
- push tag
```bash
git push origin tag vX.Y.Z
```
- push commit

### Todos

- [x] Improve user guide
- [x] Docker compose template (basic)
- [x] Add container publish to CI
- [ ] Rotating/regenerating single-user key
- [ ] Add postgres storage support
- [ ] Automated dependency/version checking?
- [ ] Integration/smoke tests
    - [ ] verify loading config
    - [ ] bootstrap doesn't overwrite config values
- [ ] pipeline cleanup job
- [ ] Add TLS? Or assume proxy?
- [ ] Add postgres storage support?
- [ ] switch to Digest Auth for api keys?
- [ ] Rotating/regenerating single-user key
- [ ] Patreon OAuth integration
- [ ] DB migration and versioning (Alembic via Flask-Migrate?)
- [ ] Custom-built ci runner image?
