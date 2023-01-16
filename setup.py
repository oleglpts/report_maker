from setuptools import setup
from setuptools.command.install import install as _install


class PostInstall(_install):
    def run(self):
        import reportmaker
        reportmaker.copy_config()
        super(PostInstall, self).run()


setup(
    name='reportmaker',
    version='0.0.1',
    packages=['reportmaker', 'reportmaker.config', 'reportmaker.utils', 'reportmaker.formats'],
    url='',
    license='',
    platforms='any',
    author='Oleg Lupats',
    author_email='oleglupats@gmail.com',
    description='Easy report maker',
    classifiers=[
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ],
    entry_points={
        'console_scripts': [
            'report = reportmaker.__main__:main'
        ]
    },
    python_requires='>=3',
    package_data={'report': ['data', 'test']},
    install_requires=[
    ],
    cmdclass={'install': PostInstall}
)
