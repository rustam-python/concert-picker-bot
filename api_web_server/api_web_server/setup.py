import setuptools

with open('README.md', "r") as readme:
    long_description = readme.read()

with open('requirements.txt') as fp:
    install_requires = fp.read()


setuptools.setup(
    name="ConcertPickerBot",
    version="1.0.0",
    author="Rustam Aliev",
    author_email="rustam.aliev.work@yandex.ru",
    description="A Telegram bot for searching of concerts based on requests to API of kudago.сom and the Last.FM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/rustam-python/concert-picker-bot",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Flask",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
    ]
)
