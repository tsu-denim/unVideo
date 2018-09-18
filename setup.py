from setuptools import setup, find_packages

setup(
    name='un-video',
    version=1,
    packages=find_packages(),
    package_data={
        '': [
            '*.py',
            '*.gz',
            '*.xsl'
        ]
    },
    entry_points={
        'console_scripts': ['unvideo-ipad=libs.video_buddy:convert_ipad',
                            'unvideo-mp3=libs.video_buddy:convert_mp3']
    }
)
