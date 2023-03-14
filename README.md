# Google Drive Monitor

This script monitors a Google Drive account, checks for files created after a
certain datetime (by default the current time), and if any of these files is
shared publicly, it changes it permissions to be private (only readable by the
owner of the Google Drive).

## Setting up permissions

- Follow the
  [Google Drive docs](https://developers.google.com/drive/api/quickstart/python#set_up_your_environment)
  and download the JSON credentials to a file named `credentials.json` in the
  same directory of the project.
- Add the `https://www.googleapis.com/auth/drive` scope

## Running

- Install a Python 3.10 virtual environment (for example, using Conda)
- Install dependencies using `pip install -r requirements.txt`
- Run using `python ./gdrive_monitor.py`

Usage:

```
❯ python gdrive_monitor.py -h
usage: gdrive_monitor.py [-h] [--check-interval CHECK_INTERVAL] [--log-level LOG_LEVEL] [--created-since CREATED_SINCE]
                         [--no-dry-run]

options:
  -h, --help            show this help message and exit
  --check-interval CHECK_INTERVAL
                        How often to check for new files
  --log-level LOG_LEVEL
  --created-since CREATED_SINCE
                        Only check files created after this time
  --no-dry-run          Actually change the permissions of files
```

## Example output

```
❯ python gdrive_monitor.py --no-dry-run --created-since '2023-03-13'
[03/13/23 22:53:16] INFO     file_cache is only supported with oauth2client<4.0.0__init__.py:49
[03/13/23 22:53:17] INFO     Default sharing settings: {'kind': 'drive#permission', 'id': '00465170165774888017', 'type': 'user', 'role': 'owner'}    gdrive_monitor.py:80
                    INFO     Checking for new files...                                                gdrive_monitor.py:113
[03/13/23 22:53:18] INFO     File: Screenshot 2022-07-06 at 17.23.27.pdf                              gdrive_monitor.py:58
                    INFO     Permissions: reader (anyone), owner (user)                               gdrive_monitor.py:61
                    INFO     Changing permission to private...                                        gdrive_monitor.py:68
                    INFO     File: test1                                                              gdrive_monitor.py:58
                    INFO     Permissions: owner (user)                                                gdrive_monitor.py:61
                    INFO     File: כרטיסי בונוס  אל על.pdf                                            gdrive_monitor.py:58
                    INFO     Permissions: owner (user)                                                gdrive_monitor.py:61
```
