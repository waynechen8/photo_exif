from typing import List
from unittest import result
from PIL import Image,  TiffImagePlugin
from PIL.Image import Exif
from PIL.ExifTags import TAGS, GPSTAGS
from pillow_heif import register_heif_opener
import os
import re
import json
# https://codeutility.org/how-to-work-with-heic-image-file-types-in-python-stack-overflow/
# https://github.com/python-pillow/Pillow/issues/5863
register_heif_opener()

def get_exif(file_name) -> Exif:
    image = Image.open(file_name)
    return image.getexif()


def get_geo(exif) -> dict:
    for key, value in TAGS.items():
        if value == "GPSInfo":
            break
    gps_info = exif.get_ifd(key)
    result_dict = {}
    for k, v in gps_info.items():
        if k in [2, 4]:
            if isinstance(v, tuple):
                v = tuple(float(t) if isinstance(t, TiffImagePlugin.IFDRational) else t for t in v)
            result_dict[GPSTAGS.get(k, k)] = v
    return result_dict
    # return {
    #     GPSTAGS.get(key, key): value
    #     for key, value in gps_info.items() if key in [2, 4]
    # }

def convert_heic_gps_filename(dir_name: str) -> List[dict]:
    filenames = os.listdir(dir_name)
    filenames_matched = [re.search("\.HEIC$|\.heic$", filename) for filename in filenames]
    HEIC_files = []
    for index, filename in enumerate(filenames_matched):
        if filename:
            HEIC_files.append(filenames[index])
    GPSInfos = []
    for filename in HEIC_files:
        image_exif = get_exif(dir_name + "/" + filename)
        if image_exif:
            geo = get_geo(image_exif)
            geo['filename'] = dir_name + "/" + filename
            GPSInfos.append(geo)
    return GPSInfos

def main():
    exif = get_exif("IMG_7036.HEIC")
    geo = get_geo(exif)
    print(geo)
    res = convert_heic_gps_filename("./images")
    with open('output.json', 'w') as f:
        json.dump(res, f)

if __name__ == '__main__':
    main()
    