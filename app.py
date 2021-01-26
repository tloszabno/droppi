#!/usr/bin/env python3

import dropbox
import os
import sqlite3
import dateutil.parser

from mytokens import DROPBOX_TOKEN
from dataclasses import dataclass
from datetime import datetime, timedelta

import config

@dataclass
class DbxFile(object):
    name: str
    path: str
    hash: str
    size: float


def is_image(file_name: str):
    return file_name.lower().endswith(tuple(config.IMAGE_EXTENTIONS))


def list_photo_files(dbx, path):
    images = filter(lambda x: is_image(x.name), dbx.files_list_folder(path=path).entries)
    return map(lambda img: DbxFile(img.name, img.path_display, img.content_hash, img.size), images)


def has_been_downloaded(connection, dbx_file):
    cursor = connection.cursor()
    result = cursor.execute('SELECT COUNT(1) FROM DOWNLOADS WHERE REMOTE_PATH=? AND HASH=?', (dbx_file.path, dbx_file.hash,))
    count = cursor.fetchone()[0]
    return count > 0


def should_be_deleted(connection, dbx_file):
    result = connection.cursor().execute('SELECT TIMESTAMP FROM DOWNLOADS WHERE REMOTE_PATH=? AND HASH=?', (dbx_file.path, dbx_file.hash,))
    for row in result:
        timestamp = dateutil.parser.parse(row[0])
        timestamp_threshold = datetime.now() - timedelta(days=config.DAYS_TO_REMOVE_AFTER_DOWNLOAD)
        return timestamp < timestamp_threshold
    return False


def mark_downloaded(connection, file, local_path):
    print("[OK]")
    params = (
        file.name,
        file.path,
        local_path,
        file.size,
        file.hash,
        datetime.now().isoformat()
    )
    connection.cursor().execute(
        f'''
        INSERT INTO DOWNLOADS(NAME, REMOTE_PATH, LOCAL_PATH, SIZE, HASH, TIMESTAMP)
        VALUES
        (?,?,?,?,?,?)
    ''', params)
    connection.commit()

def create_target_path(fs_path, file):
    target = os.path.join(fs_path, file.name)
    counter = 0
    while os.path.isfile(target):
        target = os.path.join(fs_path, file.name) + "_" + str(counter)
        counter += 1
    return target

def download(dbx, file, fs_path, conn):
    print("Downloading file %s" % file.name)
    target = create_target_path(fs_path, file)
    dbx.files_download_to_file(target, file.path)
    if os.path.isfile(target):
        if os.path.getsize(target) == file.size:
            mark_downloaded(conn, file, target)

def delete(dbx, file):
    print("Deleting file %s" % file.path)
    dbx.files_delete_v2(file.path)


def check_files(dropbox_token, dropbox_path, fs_path, conn):
    with dropbox.Dropbox(dropbox_token) as dbx:
        dbx.users_get_current_account()
        for file in list_photo_files(dbx, dropbox_path):
            if not has_been_downloaded(conn, file):
                download(dbx, file, fs_path, conn)
            if should_be_deleted(conn, file):
                delete(dbx, file)


with sqlite3.connect(config.DB_PATH) as conn:
    cursor = conn.cursor()
    print("__init_db__ creating table if not created before")
    cursor.execute('''CREATE TABLE IF NOT EXISTS DOWNLOADS
                  (ID           INTEGER PRIMARY KEY AUTOINCREMENT,
                  NAME          TEXT    NOT NULL,
                  REMOTE_PATH   TEXT    NOT NULL,
                  LOCAL_PATH    TEXT    NOT NULL,
                  SIZE          REAL    NOT NULL,
                  HASH          TEXT    NOT NULL,
                  TIMESTAMP     TEXT    NOT NULL);''')
    conn.commit()

    for config_paths in config.PATHS_CONFIGURATION:
        (dropbox_path, fs_path) = config_paths
        check_files(DROPBOX_TOKEN, dropbox_path, fs_path, conn)


