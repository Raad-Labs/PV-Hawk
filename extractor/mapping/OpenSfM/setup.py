#!/usr/bin/env python3

import os
import subprocess
import sys

import setuptools
try:
    from sphinx.setup_command import BuildDoc
except (ImportError, ModuleNotFoundError):
    BuildDoc = None
try:
    from wheel.bdist_wheel import bdist_wheel
except (ImportError, ModuleNotFoundError):
    bdist_wheel = None

VERSION = (0, 5, 2)


def version_str(version):
    return ".".join(map(str, version))


if bdist_wheel is not None:
    class platform_bdist_wheel(bdist_wheel):
        """Patched bdist_well to make sure wheels include platform tag."""

        def finalize_options(self):
            bdist_wheel.finalize_options(self)
            self.root_is_pure = False
else:
    platform_bdist_wheel = None


def configure_c_extension():
    """Configure cmake project to C extension."""
    print(
        f"Configuring for python {sys.version_info.major}.{sys.version_info.minor}..."
    )
    os.makedirs("cmake_build", exist_ok=True)
    cmake_command = [
        "cmake",
        "../opensfm/src",
        "-DPYTHON_EXECUTABLE=" + sys.executable,
    ]
    subprocess.check_call(cmake_command, cwd="cmake_build")


def build_c_extension():
    """Compile C extension."""
    print("Compiling extension...")
    subprocess.check_call(["make", "-j4"], cwd="cmake_build")


configure_c_extension()
build_c_extension()

setuptools.setup(
    name="opensfm",
    version=version_str(VERSION),
    description="A Structure from Motion library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mapillary/OpenSfM",
    project_urls={
        "Documentation": "https://docs.opensfm.org/",
    },
    author="Mapillary",
    license="BSD",
    packages=setuptools.find_packages(),
    scripts=[
        "bin/opensfm_run_all",
        "bin/opensfm",
    ],
    package_data={
        "opensfm": [
            "pybundle.*",
            "pygeo.*",
            "pygeometry.*",
            "pyrobust.*",
            "pyfeatures.*",
            "pydense.*",
            "pysfm.*",
            "pyfoundation.*",
            "pymap.*",
            "data/sensor_data.json",
            "data/bow/bow_hahog_root_uchar_10000.npz",
            "data/bow/bow_hahog_root_uchar_64.npz",
        ]
    },
    cmdclass={
        k: v for k, v in {
            "bdist_wheel": platform_bdist_wheel,
            "build_doc": BuildDoc,
        }.items() if v is not None
    },
)
