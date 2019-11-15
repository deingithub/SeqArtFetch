# SeqArtFetch


A near-universal webcomic/sequential art downloader. It visits each page like a human user, scraping and downloading all art images into a specified folder and by default only re-downloads new episodes.

[Available on PyPi](https://pypi.org/project/SeqArtFetch/).

## Usage

**`sqf init <name>`**  
Initializes a new comic called `name`. The program will ask for the directory to keep the files in, base url (the longest part of the URL common to all episodes), [CSS selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference#Selectors) for the art images, "next page" link, and some element indicating the last page has been reached, optionally for an override for the `User-Agent` header to fool some more restrictive hosts, and finally for the first episode's URL. After that, it will begin to fetch all episodes of the new comic. After the first episode has been downloaded correctly, you can abort the process and let it continue later using `sqf fetch`.

**`sqf fetch <name>`**  
Fetches the page of the last-downloaded episode and tries to find newer ones than it. Will not stop unless it hits the end, ~~horrifically crashes~~, or is interrupted with Ctrl-C.

**`sqf list`**  
Displays all known comics and their episode counts.

## Technical Details

Depends on Python 3.7+, `lxml`, `aiohttp`, and `cssselect` to do its work. Tested only on NixOS 19.09 thus far, but there is no reason it shouldn't work otherwise. If you use NixOS, you can directly get an isolated environment with all dependencies by just running `nix-shell` in the project root.