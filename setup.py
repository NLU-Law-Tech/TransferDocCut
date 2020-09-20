from setuptools import setup, setuptools
import os

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="TransferDocCut",  # Replace with your own username
    version="0.0.1",
    author='yao',
    author_email="josiriser@gmail.com",
    description="To cut TransferDoc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NLU-Law-Tech/TransferDocCut",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
)
