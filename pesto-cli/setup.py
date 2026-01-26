from setuptools import setup, find_packages

from pesto import version

entry_points = {
    'console_scripts': [
        'pesto=pesto.cli.app:main',
        'processing=pesto.ws.app:main',
    ],
}

setup(
    name='proc-factory',
    version=version.PESTO_VERSION,
    packages=find_packages(),
    maintainer='Airbus Defense & Space',
    description='Geo Processing Micro Service SDK',
    install_requires=[line for line in open('requirements.txt')],
    entry_points=entry_points,
    include_package_data=True,
)
