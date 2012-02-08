import os.path
from setuptools import setup, find_packages

def get_long_description():
    dirname = os.path.dirname(__file__)
    readme = os.path.join(dirname, 'README.txt')
    f = open(readme, 'rb')
    try:
        return f.read()
    finally:
        f.close()

setup(
    name='busyflow.pivotal',
    version='0.3.3',
    description='Pivotal API client library.',
    long_description=get_long_description(),
    author='Ignas Mikalajunas',
    author_email='ignas@nous.lt',
    url='http://github.com/nous-consulting/busyflow.pivotal/',
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Internet :: WWW/HTTP'],
    install_requires=[
        'setuptools',
        'xmlbuilder',
        'python-dateutil',
        'poster'],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['busyflow'],
    include_package_data=True,
    zip_safe=False,
    license="GPL"
)
