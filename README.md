# XPostr <!-- omit in toc -->
This is a standalone [Telegram](https://telegram.org) -> [VK](https://vk.com) crossposting app. It can handle multiple user accounts in Telegram and VK.

- [Requirements](#requirements)
- [Installation](#installation)
  - [prereqisutes](#prereqisutes)
  - [backend](#backend)
  - [frontend](#frontend)
- [Configuring](#configuring)
  - [API keys](#api-keys)
    - [Telegram](#telegram)
    - [VK](#vk)
  - [application config: `config.ini`](#application-config-configini)
  - [systemd unit](#systemd-unit)
  - [uwsgi application](#uwsgi-application)
  - [nginx](#nginx)
- [Application architecture](#application-architecture)
- [Known issues](#known-issues)
- [TODO](#todo)

# Requirements
To run backend:
- Python 3.6 (3.7 recommended)
- `uwsgi`, `uwsgi-plugin-python3`, `python3-pip` apt packages
- `pipenv` pip package

If you plan to build frontent:
- `npm`/`yarn`
- `quasar` (https://v1.quasar-framework.org/quasar-cli/installation)

# Installation
## prereqisutes
- Make sure you have Python 3.7 installed __or__ if you don't want to (or can't) install it, change `Pipfile`
  ```ini
  [requires]
  python_version = "3.7"
  ```
  to
  ```ini
  [requires]
  python_version = "3.6"
  ```
  _There is no dependencies on 3.7 changes, it's just a recommendation for performance reasons._

- Make sure you have latest version of _pip_ installed! Otherwise it can crash with weird exceptions during installation.
  ```
  apt install python3-pip
  pip install -U pip # this is important!
  ```
- Install pipenv, locally or globally. Add `--user` option to install locally.
  ```
  pip install -U pipenv
  ```
- If you want to install `uwsgi` globally, install packages `uwsgi` and `uwsgi-plugin-python3`.
- If you want to run `uwsgi` from your virtualenv -- see next step.
## backend
- Go to directory where you unpacked application source code. You should see `Pipfile` and `Pipfile.lock` there.
- Install dependencies:
  ```
  pipenv install
  ```
- If you decided to run `uwsgi` from your virtualenv -- execute `pipenv install uwsgi`
- Get your virtualenv path, you'll need it later
  ```
  pipenv --venv
  ```
## frontend
- Unpack `frontend/dist.tar.gz` to your web-root directory
- Make sure to create symlink `statics/avatars` pointing to your avatars path or set `paths.avatars` to point to `statics/avatars`. See [application config](#application-config-configini) step.

  If you want to build frontend code from source:
  - install `npm` or `yarn`
  - install [Quasar cli](https://v1.quasar-framework.org/quasar-cli/installation)
  - go to `frontend/` directory
  - use `quasar dev` to run development server or `quasar build` to build a release version

# Configuring
## API keys
First you need to register your applications on Telegram and VK.
### Telegram
- Open https://my.telegram.org and authorize there/
- In [API development tools](https://my.telegram.org/apps) you'll see your `api_id` and `api_hash` -- save them for next step.
### VK
- Open https://vk.com/apps?act=manage.
- Create new application, choose __Standalone__ as type -- this is important!
- Open _Settings_ from the left-side menu.
- You'll see your _Application ID_ and _Secret key_ -- these are your `client_id` and `client_secret` respectively, save them for next step.
- Change _Application state_ to _enabled_ and save your changes.
## application config: `config.ini`
Go to `backend` directory. Copy `config.ini.sample` to `config.ini` and make changes in sections:
- `jwt`: fill `secret` with some random string (f.e. get it with `dd  if=/dev/urandom count=1 bs=64 2>/dev/null | base64`)
- `vk`: specify your `client_id` and `client_secret`
- `telegram`: specify your `api_id` and `api_hash`. `avatars_path` is a relative uri, set it to your `avatars` directory relative to web server _document root_
- `paths`: adjust if needed
  - `db_auth` and `db_main` are full paths to sqlite database files (will be created), __directories must be writable__
  - `avatars` -- full path to directory where avatars will be downloaded, __must be writable__
  - `sessions` -- full path to directory where Telegram client will store it's session files, __must be writable__
  - `temp` -- just a temporary directory, might not exist, but path to it __must be writable__
  - `daemon_socket` -- full path to a daemon unix socket, directory __must be writable__

## systemd unit
Go to `etc/systemd/system` directory.
- Copy `xpostr-daemon.service.sample` to `xpostr-daemon.service`.
- Replace `YOUR_USER`, `APPLICATION_PATH` and `VENV_PATH` with corresponding values.
- Put `xpostr-daemon.service` file to `/etc/systemd/system`
- Execute `systemctl daemon-reload` for systemd to pick up new unit
- Enable (for autostart) and start it:
  ```
  systemctl enable xpostr-daemon
  systemctl start xpostr-daemon
  ```

## uwsgi application
Go to `etc/uwsgi/apps-available`. Copy `xpostr-web.ini.sample` to `xpostr-web.ini`. Replace `APPLICATION_PATH`, `VENV_PATH` and `USER` with corresponding values.

Now, if you want to run `uwsgi` from virtualenv -- repeat previous part steps replacing all mentions of `xpostr-daemon` with `xpostr-web`.

Or, if you use `uwsgi` installed from apt, add your app:
```
cp etc/uwsgi/apps-available/xpostr-web.ini /etc/uwsgi/apps-available
ln -s /etc/uwsgi/apps-available/xpostr-web.ini /etc/uwsgi/apps-enabled
systemctl restart uwsgi
```

## nginx
Use `etc/nginx/sites-available/xpostr-web.conf.sample` as a reference to configure your web server.

There is no reason to keep web ui files at `frontend/dist/spa`. You can place them anywhere you wish, just remember to adjust `telegram.avatars` (and possibly `paths.avatars`) in `config.ini` respectively.

# Application architecture

__TODO__

# Known issues
- Non user-friendly VK authentication process: unfortunately VK has crippled permission system, so some API are available __only__ if `redirect_uri` of OAuth process is points to _api.vk.com_ (so called standalone applications).
- Wide permission list for VK: unfortunately VK has crippled permission system -- 1 permission controls 1 API method. Regardless of where you plan to post, to user personal feed or to any of his groups, you need to get one permission to access all of them. Same for photos/documents.
- Complete Telegram authentication process: unfortunately Telegram restricts bots from reading channel messages (even for public ones), so need to use Client API here with complete authentication process.
- Telegram voice messages: uploads successfully but VK doesn't attach them, so message looks empty (probably also need conversion to MP3).
- Telegram message media: sometimes telegram server kicks client when downloading media -- this may lead to missing attachment or fail to post to VK.
- Web UI: On JWT expiration authorized state isn't preperly reset
- Web UI: Dropdowns in _Create new_ dialog are cropped to dialog borders. Quasar issue, waiting for fix.

# TODO
- [ ] handle case when Telegram user revokes app access from another client
- [ ] handle case when VK user revokes app access after it's been granted
- [ ] replace `requests` with `aiohttp`
- [ ] add transitions use in UI
- [ ] implement token refresh in UI
- [ ] logging config
- [ ] per connection settings:
  - [ ] add/attach forwarded from
  - [ ] add/attach 'in reply to'
  - [ ] some basic filtering
- [ ] backend `lib.xpost` is a bloody mess. refactor it
- [ ] merge web-service with daemon code?
