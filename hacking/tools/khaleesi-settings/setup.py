from setuptools import setup, find_packages
from os.path import join, dirname, abspath
import khaleesi


prj_dir = dirname(abspath(__file__))
setup(
    name='khaleesi-settings',
    version=khaleesi.__VERSION__,
    packages=find_packages(),
    long_description=open(join(prj_dir, 'README.rst')).read(),
    entry_points={
        'console_scripts': ['khaleesi-settings = khaleesi.core:main']
    },
    install_requires=[
        'docopt',
        'PyYAML',
        'configure'
    ],
    author='Sunil Thaha',
    author_email='sthaha@redhat.com'
)
