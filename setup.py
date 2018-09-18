from setuptools import setup, find_packages

setup(
    name='un-video',
    version=1,
    packages=find_packages(),
    package_data={
        '': [
            '*.py'
        ]
    },
    install_requires=[
        'botocore',
        'boto3',
        'setuptools',
        'wheel',
        'eyed3',
        'python-magic'
    ],
    entry_points={
        'console_scripts': ['unvideo-ipad=libs.video_buddy:convert_ipad',
                            'unvideo-mp3=libs.video_buddy:convert_mp3']
    }
)
