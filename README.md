![Made with Python](https://forthebadge.com/images/badges/made-with-python.svg)

```ascii
 █████╗ ███╗   ██╗██╗███╗   ███╗███████╗    ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
██╔══██╗████╗  ██║██║████╗ ████║██╔════╝    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
███████║██╔██╗ ██║██║██╔████╔██║█████╗      ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
██╔══██║██║╚██╗██║██║██║╚██╔╝██║██╔══╝      ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
██║  ██║██║ ╚████║██║██║ ╚═╝ ██║███████╗    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝

       by HectorH06 (@HectorH06)          version 0.0
```

### General Description

This is an scraper for anime that searches within the HTML of anitaku pages and extracts the best quality links for each episode.

```diff
- EDUCATIONAL PURPOSES ONLY
```

## Installation

1. Install requirements with the following commands:

   `pip install beautifulsoup4`
   `pip install requests`

## Features

- Download whole series
   - One by One
   - Massively
- Params:
   - Link from anitaku for the series
   - Series name
   - First and last episode
- Manages corner cases for not standarized URLs

## Future Features

- GUI
- May turn massive download arguments to an object instead of dict