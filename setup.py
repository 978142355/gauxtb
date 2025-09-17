import sys
from setuptools import setup

python_min_version = (3, 9)

if sys.version_info < python_min_version:
    raise SystemExit(
        'Python %d.%d or later is required!' % python_min_version
    )

setup(
)
