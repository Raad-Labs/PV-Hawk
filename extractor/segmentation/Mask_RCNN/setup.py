"""
The build/compilations setup

>> pip install -r requirements.txt
>> pip install -e .
"""
import logging
from pathlib import Path
from setuptools import setup


def _parse_requirements(file_path):
    try:
        return [
            line.strip()
            for line in Path(file_path).read_text().splitlines()
            if line.strip() and not line.startswith('#')
        ]
    except Exception:
        logging.warning('Failed to load requirements file.')
        return []


install_reqs = _parse_requirements("requirements.txt")

setup(
    name='mask-rcnn',
    version='2.2',
    url='https://github.com/Raad-Labs/PV-Hawk',
    author='Matterport / Raad Labs',
    license='MIT',
    description='Mask R-CNN for object detection and instance segmentation (TF2 fork)',
    packages=["mrcnn"],
    install_requires=install_reqs,
    include_package_data=True,
    python_requires='>=3.9',
    long_description="""TF2-compatible fork of Mask R-CNN for PV module segmentation.
Uses tensorflow.keras instead of standalone keras.""",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords="image instance segmentation object detection mask rcnn r-cnn tensorflow keras",
)
