from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='OSGRMATT',
    version='0.1.8',
    author='theMizza',
    author_email='dirtymeff@yandex.ru',
    description='Simple framework to fast build selenium (with remote selenium grid as option) and api tests.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'Faker==20.0.3',
        'opencv-python==4.9.0.80',
        'pyodbc==5.0.1',
        'pyTelegramBotAPI==4.14.1',
        'pytest==7.4.3',
        'pytest-html==4.1.1',
        'requests==2.31.0',
        'selenium==4.15.2',
        'webdriver-manager==4.0.1',
        'SQLAlchemy==2.0.23',
        'exchangelib~=5.4.1',
        'numpy~=1.24.4',
        'beautifulsoup4==4.12.3',
        'bs4==0.0.2',
        'python-dotenv~=1.0.1'
    ],
    entry_points={
        'console_scripts': [
            'osgrmatt = OSGRMATT.cli:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.8'
    ],
    keywords='selenium api tests',
    project_urls={
        'GitHub': 'https://github.com/theMizza/OSGRMATT'
    },
    python_requires='>=3.8'
)
