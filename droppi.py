#!/usr/bin/env python3

import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

import dateutil.parser
import dropbox

import config

log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL)


@dataclass
class DbxFile(object):
    name: str
    path: str
    hash: str
    size: float


def is_enabled_extension(file_name: str):
    return file_name.lower().endswith(tuple(config.FILE_EXTENSIONS_TO_SYNC))


def list_files_with_enabled_extentions(dbx, path):
    files = filter(lambda x: is_enabled_extension(x.name), dbx.files_list_folder(path=path).entries)
    return map(lambda file: DbxFile(file.name, file.path_display, file.content_hash, file.size), files)


def has_been_downloaded(connection, dbx_file):
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(1) FROM DOWNLOADS WHERE REMOTE_PATH=? AND HASH=?', (dbx_file.path, dbx_file.hash,))
    count = cursor.fetchone()[0]
    return count > 0


def should_be_deleted(connection, dbx_file):
    result = connection.cursor().execute('SELECT TIMESTAMP FROM DOWNLOADS WHERE REMOTE_PATH=? AND HASH=?',
                                         (dbx_file.path, dbx_file.hash,))
    for row in result:
        timestamp = dateutil.parser.parse(row[0])
        timestamp_threshold = datetime.now() - timedelta(days=config.DAYS_TO_REMOVE_AFTER_DOWNLOAD)
        return timestamp < timestamp_threshold
    return False


def mark_downloaded(connection, file, local_path):
    log.info(f"Downloaded file {file} to {local_path}")
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
    log.debug("Downloading file %s" % file.name)
    target = create_target_path(fs_path, file)
    dbx.files_download_to_file(target, file.path)
    if os.path.isfile(target):
        if os.path.getsize(target) == file.size:
            mark_downloaded(conn, file, target)


def delete(dbx, file):
    log.info("Deleting file %s" % file.path)
    dbx.files_delete_v2(file.path)


def handle_config_path(dropbox_token, dropbox_path, fs_path, conn):
    log.info(f"Going with dropbox_path={dropbox_path} and fs_path={fs_path}")
    with dropbox.Dropbox(dropbox_token) as dbx:
        dbx.users_get_current_account()
        for file in list_files_with_enabled_extentions(dbx, dropbox_path):
            if not has_been_downloaded(conn, file):
                download(dbx, file, fs_path, conn)
            if should_be_deleted(conn, file):
                delete(dbx, file)


def main():
    with sqlite3.connect(config.DB_PATH) as conn:
        log.info("Creating table if not created before")
        conn.cursor().execute('''CREATE TABLE IF NOT EXISTS DOWNLOADS
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
            handle_config_path(config.DROPBOX_TOKEN, dropbox_path, fs_path, conn)


if __name__ == '__main__':
    main()
