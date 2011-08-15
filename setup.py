from setuptools import setup, find_packages

setup(
    name='busyflow.pivotal',
    version='0.1',
    description='Pivotal API client library.',
    author='Ignas Mikalajunas',
    author_email='ignas@nous.lt',
    url='http://github.com/Ignas/busyflow.pivotal/',
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Internet :: WWW/HTTP'],
    install_requires=[
        'setuptools',
        'xmlbuilder'],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['busyflow'],
    include_package_data=True,
    zip_safe=False,
    license="GPL"
)
