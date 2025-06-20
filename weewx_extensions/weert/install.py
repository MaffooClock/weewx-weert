#
#    Copyright (c) 2025 Matthew Clark
#
#    See the file LICENSE.txt for your full rights.
#
"""Installer for WeeRT"""

from .bin.user.config import config_defaults
from weecfg.extension import ExtensionInstaller


def loader():
    return WeertInstaller()


class WeertInstaller(ExtensionInstaller):
    def __init__(self):
        super(WeertInstaller, self).__init__(
            version='0.1',
            name='weert',
            description='A component of WeeRT server',
            author='Tom Keffer',
            author_email='tkeffer@gmail.com',
            restful_services='user.weert.WeeRT',
            config=config_defaults,
            files=[('bin/user', ['bin/user/weert.py'])]
        )
