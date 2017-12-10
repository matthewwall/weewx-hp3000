# installer for hp3000 driver
# Copyright 2016 Matthew Wall
# Distributed under the terms of the GNU Public License (GPLv3)

from setup import ExtensionInstaller

def loader():
    return HP3000Installer()

class HP3000Installer(ExtensionInstaller):
    def __init__(self):
        super(HP3000Installer, self).__init__(
            version="0.6",
            name='hp3000',
            description='Collect data from HP-3000 temperature/humidity sensors',
            author="Matthew Wall",
            author_email="mwall@users.sourceforge.net",
            files=[('bin/user', ['bin/user/hp3000.py'])])
