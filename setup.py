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
    url='',
    license='MIT',
    author=metadata["version"],
    author_email=metadata["author_email"],
    description='',
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
    }
)
