# installer for ws3000 driver
# Copyright 2016 Matthew Wall

from setup import ExtensionInstaller

def loader():
    return WS3000Installer()

class WS3000Installer(ExtensionInstaller):
    def __init__(self):
        super(WS3000Installer, self).__init__(
            version="0.1",
            name='ws3000',
            description='Collect data from WS-3000 T/H sensors',
            author="Matthew Wall",
            author_email="mwall@users.sourceforge.net",
            files=[('bin/user', ['bin/user/ws3000.py'])]
            )
