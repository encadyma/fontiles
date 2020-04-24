# Fontiles
Open source font server (MVP in development), written for self hosting.

![Fontiles (MVP)](https://i.fluffy.cc/mx60xwGKXt8shTn1nZqwCnMfGcPfXKFP.png)

Currently, Fontiles is an MVP in development, so it is not recommended for production use and is subject to breaking changes. If you would like support, please open a Github issue and tag me (@encadyma).

## What does it have?

- **The ability to serve your font library over the web**
- A simple, clean web interface for browsing and downloading fonts
- A lean API for embedding webfonts via CSS
- Machine-digestible (JSON) font configurations for dynamic font-loading apps
- Simple, human-readable configurations, alongside a built-in validation tool

## What is planned?

- Expanded web interface for searching, bookmarking, and managing fonts
- User accounts for saving fonts and convenient embedding
- Production-ready web serving
- Easy, reproducible deployments via Docker, Kubernetes, etc.

## Quickstart

You will need Python 3 and Flask. You may also need to install dependencies such as PyYAML.

To get started with your own setup, you can fork the Fontiles server. The starting point for new configurations is `app.yaml`, which defines basic metadata about the server and specifies where Fontiles should look for fonts.

You will also need to specify at least one fonts folder. An example is already provided in this repository under `fonts/`.

To add a new font family, create a directory and place all the font assets inside [1]. Create a new Fontiles configuration `font.yaml` where you can specify important font metadata and the font family's members [(example config)](https://github.com/encadyma/fontiles/blob/master/fonts/Source%20Sans%20Pro/font.yaml).

You can check that your configuration works by running `python3 checker.py`, which will validate your config and return what Fontiles will see.

From there, you can run `app.py` through `flask run`, which will bring up a web server that will serve all of your fonts!

[1] Font assets can be retrieved for free from other sources such as Google Fonts.
