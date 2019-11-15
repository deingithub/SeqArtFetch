import sys
import os
import configparser
import asyncio
import urllib.parse

import aiohttp
from lxml import html, etree

CONFIG_PATH = f"{os.environ['HOME']}/.config/seqartfetch.ini"

VERSION = "0.2.3"

USAGE = f"""SeqArtFetch {VERSION}

About
  A semi-universal webcomic/sequential art downloader, licensed under MIT.
  Brought to you by Dingenskirchen Systems.

Usage
  sqf fetch <comic>         Fetch newest episodes of existing <comic>
  sqf init <comic>          Interactively initialize <comic>
  sqf list                  Display current configuration

Links
  GitHub (source, issues)   https://github.com/deingithub/SeqArtFetch
  PyPi (downloads)          https://pypi.org/project/SeqArtFetch/
"""


async def main():
    if len(sys.argv) == 1:
        print(USAGE)
        exit(0)
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    if sys.argv[1] == "fetch":
        if len(sys.argv) == 3 and sys.argv[2] in cfg:
            await do_fetch(cfg[sys.argv[2]])
        else:
            print("Missing or unknown comic name, exiting")
            exit(1)

    elif sys.argv[1] == "init":
        if len(sys.argv) == 3:
            await do_init(cfg, sys.argv[2])
        else:
            print("Missing comic name, exiting")
            exit(1)

    elif sys.argv[1] == "list":
        do_config_print(cfg)

    else:
        print(USAGE)
        exit(0)


async def do_fetch(cfg):
    file_name = os.path.splitext(sorted(os.listdir(cfg["path"]))[-1])[0]
    last_episode = int(file_name.split(" ")[0].split("-")[0])
    last_slug = " ".join(file_name.split(" ")[1:])
    await fetch_episodes(cfg, cfg["base_url"] + last_slug, last_episode)


async def do_init(cfg, comicname):
    if comicname in cfg:
        print(f"Duplicate comic name {comicname}, exiting")
        exit(1)
    print(f"Initializing {comicname}...")
    cfg[comicname] = {}
    path = input("Episodes directory> ")
    if not os.path.isdir(path):
        if os.path.exists(path):
            print("Path already exists, but is a file; exiting")
            exit(1)
        print("Directory doesn't exist, creating...")
        os.makedirs(path)

    cfg[comicname]["path"] = path
    cfg[comicname]["base_url"] = input("Base URL of all episodes> ")
    cfg[comicname]["image"] = input("CSS selector for the image> ")
    cfg[comicname]["next_link"] = input("CSS selector for the next episode link> ")
    cfg[comicname]["last_page"] = input("CSS selector for the last page> ")
    cfg[comicname]["override_ua"] = input("User-Agent (leave empty for no override)> ")
    if len(cfg[comicname]["override_ua"]) == 0:
        cfg.remove_option(comicname, "override_ua")

    with open(CONFIG_PATH, "w") as configfile:
        cfg.write(configfile)
    first_url = input("First Episode URL> ")
    await fetch_episodes(cfg[comicname], first_url, 1)


def do_config_print(cfg):
    if len(cfg.sections()) == 0:
        print("No configuration stored, exiting")
        exit(0)
    print(f"Configuration file: {CONFIG_PATH}\n")
    for sec in cfg.sections():
        print(
            f"{sec} ({len(os.listdir(cfg[sec]['path']))} files)\n"
            + f"  {cfg[sec]['base_url']} => {cfg[sec]['path']}"
        )


async def fetch_episodes(cfg, url, episode):
    async with aiohttp.ClientSession() as session:
        failures = []
        headers = {"Connection": "close"}
        if "override_ua" in cfg:
            headers["User-Agent"] = cfg["override_ua"]

        while True:
            async with session.get(url, headers=headers) as response:
                print(f"Fetching #{episode:05} @ {url}")

                if response.status >= 400:
                    failures.append((episode, url))
                    print(f"Failure: Non-OK status {response.status}")
                    await asyncio.sleep(0.5)
                    next

                tree = html.fromstring(await response.text())
                image_elems = tree.cssselect(cfg["image"])
                if len(image_elems) == 0:
                    failures.append((episode, url))
                    print("Failure: No image found")
                    await asyncio.sleep(0.5)
                    next

                for index, elem in enumerate(image_elems):
                    link = elem.attrib["src"]
                    image_url = urllib.parse.urljoin(cfg["base_url"], link)
                    async with session.get(image_url, headers=headers) as image:
                        if image.status >= 400:
                            failures.append((episode, image_url))
                            print(
                                f"Failure: Image {image_url} returned non-ok status {image.status}"
                            )
                        binary_data = await image.read()

                        file_name = cfg["path"] + "/"
                        if len(image_elems) == 1:
                            file_name += f"{episode:05} "
                        else:
                            file_name += f"{episode:05}-{index} "

                        file_name += (
                            f"{url[len(cfg['base_url']):]}.{image_url.split('.')[-1]}"
                        )

                        with open(file_name, "wb") as image_file:
                            image_file.write(binary_data)

                if len(tree.cssselect(cfg["last_page"])) > 0:
                    print("Reached last page, exiting...")
                    break

                # we assert that a next link exists
                next_link = tree.cssselect(cfg["next_link"])[0]

                url = urllib.parse.urljoin(cfg["base_url"], next_link.attrib["href"])
                episode += 1
                await asyncio.sleep(1)

        if failures:
            print(f"Experienced {len(failures)} failures:")
            for episode, url in failures:
                print(f"#{episode:05} ({url})")


def totally_not_main():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted, exiting")


if __name__ == "__main__":
    totally_not_main()
