import logging
import os
import re
import zipfile
from os import path
import plistlib

from .. import schemas


def scan_directory(base_path: path):
    ipas: list[schemas.IPA] = []
    with os.scandir(base_path) as files:
        for f in filter(lambda f: os.path.basename(f).endswith('.ipa'), files):
            try:
                plist = None

                if zipfile.is_zipfile(f):
                    with zipfile.ZipFile(f) as ipa_zip:
                        info_plist_pattern = re.compile(r"Payload/.*\.app/Info\.plist")
                        info_plist_pathstr: str = next(
                            filter(lambda x: info_plist_pattern.match(x), ipa_zip.namelist()))
                        with ipa_zip.open(info_plist_pathstr) as info_plist:
                            plist = plistlib.load(info_plist)
                else:
                    with open(os.path.join(f, 'Info.plist'), 'rb') as fp:
                        plist = plistlib.load(fp)

                ipa: schemas.IPA = schemas.IPA(path=f,
                                               bundle_id=plist['CFBundleIdentifier'],
                                               minimum_os_version=plist['MinimumOSVersion'],
                                               supported_platforms=plist['CFBundleSupportedPlatforms'],
                                               bundle_name=plist['CFBundleName'],
                                               bundle_version=plist['CFBundleVersion']
                                               )
                ipas.append(ipa)
            except FileNotFoundError:
                continue
            except NotADirectoryError:
                continue
            except KeyError as e:
                logging.log(logging.WARNING, f"{f}/Info.plist is missing required key: {e}")
                continue
    return ipas
