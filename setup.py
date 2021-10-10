"""
The MIT License (MIT)

Copyright (c) [2015-2021] [Andrew Annex]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__author__ = "AndrewAnnex"

from setuptools import setup, Command, find_packages, Extension
from setuptools.command.install import install
from setuptools.command.build_py import build_py
from setuptools.dist import Distribution
import os
import sys
from pathlib import Path
from itertools import chain

DEV_CI_DEPENDENCIES = [
    'numpy>=1.17.0;python_version>="3.6"',
    "pytest>=2.9.0",
    "pandas>=0.24.0",
    "coverage>=5.1.0",
    "codecov>=2.1.0",
    "twine>=3.3.0",
    "wheel",
    "black",
]

TEST_DEPENDENCIES = [
    'numpy>=1.17.0;python_version>="3.6"',
    "pytest>=2.9.0",
    "pandas>=0.24.0",
]
DEPENDENCIES = [
    'numpy>=1.17.0;python_version>="3.6"',
]
REQUIRES = ["numpy"]


def glob(dir, ext="*.c") -> list:
    return list(map(str, Path(dir).glob(ext)))


CSPICE_SRC_DIR = "CSPICE_SRC_DIR"
# Get current working directory
root_dir = str(Path().cwd())
# Make the directory path for cspice
cspice_dir = os.environ.get(CSPICE_SRC_DIR, os.path.join(root_dir, "cspice/"))
# get system
system = platform.system()
if system == 'Windows':
    extra_compile_args = ["-D_COMPLEX_DEFINED", "-DMSDOS", "-DOMIT_BLANK_CC", "-DNON_ANSI_STDIO"]
else:
    extra_compile_args = ["-fPIC", "-ansi"]


if not Path(cspice_dir).exists():
    from get_spice import GetCSPICE, copy_supplements, apply_patches

    GetCSPICE()
    apply_patches()

cspice_module = Extension(
    "cspice",
    language="c",
    sources=[
        *chain(
            glob("./cspice/src/cspice/"),
            glob("./cspice/src/csupport/"),
        )
    ],
    include_dirs=[
        "./cspice/include/",
        "./cspice/src/cspice/",
        "./cspice/src/csupport/",
    ],
    extra_compile_args=["-fPIC", "-ansi"],
)

cmdclass = {}

# https://stackoverflow.com/questions/45150304/how-to-force-a-python-wheel-to-be-platform-specific-when-building-it
# http://lepture.com/en/2014/python-on-a-hard-wheel
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class generic_bdist_wheel(_bdist_wheel):
        """
        override for bdist_wheel
        """

        def run(self):
            _bdist_wheel.run(self)

        def finalize_options(self) -> None:
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

        def get_tag(self) -> (str, str, str):
            python, abi, plat = _bdist_wheel.get_tag(self)
            return "py3", "none", plat

    # add our override to the cmdclass dict so we can inject this behavior
    cmdclass["bdist_wheel"] = generic_bdist_wheel

except ImportError:
    # we don't have wheel installed so there is nothing to change
    pass

readme = open("README.rst", "r")
readmetext = readme.read()
readme.close()

setup(
    name="spiceypy",
    version="4.0.2",
    license="MIT",
    author="Andrew Annex",
    author_email="ama6fy@virginia.edu",
    description="A Python Wrapper for the NAIF CSPICE Toolkit",
    long_description=readmetext,
    python_requires=">=3.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
    keywords=["spiceypy", "spice", "naif", "jpl", "space", "geometry", "ephemeris"],
    url="https://github.com/AndrewAnnex/SpiceyPy",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: Microsoft :: Windows",
    ],
    packages=find_packages(include="spiceypy"),
    include_package_data=True,
    zip_safe=False,
    ext_modules=[cspice_module],
    package_data={
        "spiceypy": ["utils/*.so.*", "utils/*.dll", "utils/*.dylib"],
        "": ["get_spice.py", "LICENSE"],
    },
    setup_requires=DEPENDENCIES,
    install_requires=DEPENDENCIES,
    requires=REQUIRES,
    tests_require=TEST_DEPENDENCIES,
    cmdclass=cmdclass,
    test_suite="spiceypy.tests.test_wrapper.py",
    extras_require={"testing": TEST_DEPENDENCIES, "dev": DEV_CI_DEPENDENCIES},
)
