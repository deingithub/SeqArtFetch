from setuptools import setup, find_packages

setup(
    name="SeqArtFetch",
    description="A near-universal webcomic/sequential art downloader.",
    author="deing",
    author_email="admin@15318.de",
    version="0.1.0",
    license="MIT",
    url="https://github.com/deingithub/SeqArtFetch",
    packages=["."],
    zip_safe=True,
    install_requires=["aiohttp", "cssselect", "lxml"],
    entry_points={"console_scripts": ["sqf=main:totally_not_main"]},
)
