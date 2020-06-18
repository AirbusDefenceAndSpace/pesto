from setuptools import setup, find_packages

with open('README.md', "r") as readme_file:
    readme = str(readme_file.read())

with open('requirements.txt', 'r') as requirements_file:
    install_requires = [line for line in requirements_file]

setup(
    name="{{cookiecutter.project_sname}}",
    version="{{cookiecutter.project_version}}",
    description="{{cookiecutter.project_short_description}}",
    long_description=readme + '\n\n',
    author="{{cookiecutter.maintainer_fullname}}",
    author_email='{{cookiecutter.maintainer_email}}',
    url="",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    keywords=["pesto-project"],
)
