import logging

"""
    Token to your dropbox account 
"""
DROPBOX_TOKEN = "XXXXXX"


"""
    PATHS_CONFIGURATION should contain list of tuples with path on dropbox remote folder and local folder
    For instance:
    PATHS_CONFIGURATION = [
        ('/Camera Uploads', '/home/xxx/photos/to_check'),
        ('/Camera Uploads (1)', '/home/xxx/photos/to_check')
    ]
"""
PATHS_CONFIGURATION = [
    ('/Camera Uploads', '/home/xxx/photos/to_check'),
    ('/Camera Uploads (1)', '/home/xxx/photos/to_check')
]

"""
    IMAGE_EXTENSIONS contains extensions of images that we want to synchronize. 
    Files with other extensions will not be downloaded.  
"""
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


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
