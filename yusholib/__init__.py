__name__ = "yusholib"
__author__ = "yusho"
__license__ = "MIT"
__version__ = "0.0.1a"

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import platform, sys
from typing import Literal, NamedTuple
from . import *

class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int

version_info: VersionInfo = VersionInfo(major=0, minor=0, micro=3, releaselevel='alpha', serial=0)

def show_version() -> None:
    lines = []
    lines.append("* Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(sys.version_info))
    lines.append("* yusholib v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(version_info))
    uname = platform.uname()
    lines.append('* system info: {0.system} {0.release} {0.version}'.format(uname))
    print("\n".join(lines))
    return lines # type: ignore