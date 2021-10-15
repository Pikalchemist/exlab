import setuptools
from distutils.core import setup
# from Cython.Build import cythonize

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="exlab",
    version="0.1.2",
    author="Alexandre Manoury",
    author_email="alex@pika.tf",
    description="A Experimental Laboratory suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pikalchemist/exlab",
    # ext_modules=cythonize("lems/lib/operations.pyx"),
    packages=setuptools.find_packages(exclude=('tests', 'examples')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["coloredlogs", "executing", "Flask", "Flask-Cors", "matplotlib", "numpy", "Pillow", "PyYAML", "tabulate"]
)
