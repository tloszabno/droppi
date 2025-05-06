# DropPi

## Description

I like a lot the dropbox cloud. I use their photos synchronisation and I think it is great.
However, it has one drawback - It has limited space in the free version.

Why not sync photos with dropbox and download that photos to folder on my NAS which is hosted on raspberrypi.

And that kinds is the story how I wrote your future photo synchronizer.


### How does it work?

DropPi just:
1. Connects to your dropbox account (via dropbox token)
2. Downloads files from the remote location to local (which you selected)
3. After configured number of days, deletes downloaded files


### Configuration

Please see `config.py` file. It should be well documented.

The simples way to use this is to set variable `PATHS_CONFIGURATION` and `DROPBOX_TOKEN`.

Sample configuration:
```py
import logging

DROPBOX_TOKEN = "YOUR_TOKEN_GOES_HERE"

"""
    PATHS_CONFIGURATION should contain list of tuples with path on dropbox remote folder and local folder
    For instance:
    PATHS_CONFIGURATION = [
        ('/Camera Uploads', '/home/xxx/photos/to_check'),
        ('/Camera Uploads (1)', '/home/xxx/photos/to_check')
    ]
"""
PATHS_CONFIGURATION = [
    ('/Camera Uploads', '/home/pi/NAS/photos/to_review'),
    ('/Camera Uploads (1)', '/home/pi/NAS/photos/to_review')
]

"""
    FILE_EXTENSIONS_TO_SYNC contains extensions of files that we want to synchronize.
    Files with other extensions will not be downloaded.
"""
FILE_EXTENSIONS_TO_SYNC = [".jpg", ".jpeg", ".png"]


"""
    DAYS_TO_REMOVE_AFTER_DOWNLOAD
    Photos are not deleted just after download to some local path.
    By this variable you can set that photos should be deleted 5 or 100 days after file download.
    If you set this to 0 it will be deleted instantaneously.
"""
DAYS_TO_REMOVE_AFTER_DOWNLOAD = 14

"""
    DB_PATH is path to local database when all information about downloaded files are stored in.
    By default db will be in the folder of project but there is no reason why this could not be
    set to for instance: /home/xx/photos.dbx.sqlite
"""
DB_PATH = 'db.sqlite'



LOG_LEVEL = logging.INFO


```


### How to obtain token to the dropbox account?

1. Please enter https://www.dropbox.com/developers/apps?_tk=pilot_lp&_ad=topbar4&_camp=myapps
2. Click _Create app_
3. Select _Scoped access_
4. Select _Full Dropbox_
5. in name put _drpi_ with some suffix or any name you would remember for this app
6. Click _Create_
7. Change _Access token expiration_ to _No expiration_
8. In section _Generated access token_ click _Generate_
9. Copy the token and put in `config.py`

### Requirements

* Python 3
* pipenv (in raspbian can be installed by `sudo apt install python3-pipenv -y`)

### How to install this?

Just clone repository to folder on your drive with command: `git clone https://github.com/tloszabno/droppi.git`

# Running

1. run `pipenv install`
2. run `pipenv shell` and `./droppi.py` or `pipenv run ./droppi.py`

# Adding to cron

You should DropPi this to your cron to automatically sync dropbox with your folder

In the terminal enter:
```
cron -e
```

end at the end of file put:
```
0,30 * * * * /path/to/place/with/droppi/run.sh
```
this will run DropPi every 30 minutes.

