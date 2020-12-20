#!/usr/bin/env python3

import dropbox
import os
from mytokens import DROPBOX_TOKEN
from dataclasses import dataclass, field

DROPBOX_PATH = '/Camera Uploads'
FS_PATH = '/home/tomek/tmp'

image_extensions = [".jpg", ".jpeg", ".png"]

@dataclass
class DbxFile(object):
    name: str
    path: str
    hash: str

def is_image(file_name: str):
    return file_name.lower().endswith(tuple(image_extensions))


def list_photo_files(dbx, path):
    images = filter(lambda x: is_image(x.name), dbx.files_list_folder(path=path).entries)
    return map(lambda img: DbxFile(img.name, img.path_display, img.content_hash), images)


def has_been_copied(dbx_file):
    return False  # TODO: impement db and fs!!!


def should_be_deleted(dbx_file):
    return False  # TODO: impement db


def download(dropbox_token, dropbox_path, fs_path):
    with dropbox.Dropbox(dropbox_token) as dbx:
        dbx.users_get_current_account()
        for file in list_photo_files(dbx, dropbox_path):
            if not has_been_copied(file):
                print("Downloading file %s" % file.path)
                dbx.files_download_to_file(os.path.join(fs_path, file.name), file.path)


download(DROPBOX_TOKEN, DROPBOX_PATH, FS_PATH)