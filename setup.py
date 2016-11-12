# _*_ coding: utf-8 _*_
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-abtoast',
    version='1.0.0',
    author='Hiten Sharma',
    author_email='sharmahiten3@gmail.com',
    packages=find_packages(),
    url='https://github.com/htadg/ABToast',
    license='MIT License',
    description='ABToast is an A/B Testing app that is developed in django.',
    long_description=open('README.md').read(),
    zip_safe=False,
)