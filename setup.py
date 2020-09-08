import setuptools
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rocklog",
    version="0.0.1",
    author="Thilo Schild",
    author_email="work@thilo-schild.de",
    description="collects Logs and presents them in a web app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiloschild/RockLog",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    packages=setuptools.find_packages(),
    install_requires=['json', 'pandas', 'Dash', 'Plotly', 'easygui'],
    python_requires='>=3.6',
    entry_points={

        'console_scripts': [
            'start_app = RockLog.app:main'
        ],
        
    }
)