from setuptools import setup, find_packages
from pathlib import Path
import re


with open(str(Path(__file__).parents[0] / "cubelang" / "__init__.py")) as f:
    init_file = f.read()
    metadata = dict(re.findall(r"^__([a-z_]+)__\s*=\s*\"(.*)\"$", init_file,
                               re.MULTILINE))


setup(
    name='CubeLang',
    version=metadata["version"],
    packages=find_packages(),
    package_data={'': ["../data/*.lark"]},
    url='https://github.com/poletaevvlad/CubeLang',
    license='MIT',
    author=metadata["version"],
    author_email=metadata["author_email"],
    description="Domain-specific programming language made for solving twisting cube puzzles",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        "lark-parser",
        "termcolor"
    ],
    entry_points={
        "console_scripts": [
            "cubelang = cubelang.cli.entry:main",
            "cubelang-scramble = cubelang.scrambler:main"
        ]
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ]
)
