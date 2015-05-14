from setuptools import setup, find_packages
from os.path import join, dirname, abspath
import kcli


prj_dir = dirname(abspath(__file__))
setup(
    name='kcli',
    version=kcli.__VERSION__,
    packages=find_packages(),
    long_description=open(join(prj_dir, 'README.rst')).read(),
    entry_points={
        'console_scripts': ['kcli = kcli.core:main']
    },
    install_requires=[
        'ansible',
    ],
    author='Yair Fried',
    author_email='yfried@redhat.com'
)
