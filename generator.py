import yaml
import os
from checker import ensure_file_exists

APP_VERSION = "1.0.0"
APP_CONFIG = None

def fetch_config():
    global APP_CONFIG
    if APP_CONFIG is None:
        APP_CONFIG = generate_config()

    return APP_CONFIG

def fetch_raw_config():
    assert ensure_file_exists('app.yaml')

    with open('app.yaml') as cf:
        return yaml.load(cf, Loader=yaml.FullLoader)

def generate_config(include_raw=False):
    """
    Return an application config based on a correct
    app.yaml with the following properties:

    ```
    name
    appVersion
    description
    hoster
    host:
    fonts
    - <font-name>:
        name
        slug
        configPath ($HOST/fonts/$FONT_SLUG/font.json)
        licensePath (if specified)
    ```
    """
    
    cfg = fetch_raw_config()

    generated_cfg = {
        "name": cfg["name"],
        "appVersion": APP_VERSION,
        "description": "Powered by Fontiles" if not "description" in cfg else cfg["description"],
        "hoster": "Webmaster" if not "hoster" in cfg else cfg["hoster"],
        "host": cfg["host"],
        "fonts": {},
    }

    # TODO: return all fonts!
    for font_name in cfg['fonts']:
        font_path = None
        for path in cfg["font_paths"]:
            if os.path.isdir(os.path.join(path, font_name)):
                font_path = os.path.join(path, font_name)
        
        with open(os.path.join(font_path, 'font.yaml')) as fcf:
            fcfg = yaml.load(fcf, Loader=yaml.FullLoader)

        generated_cfg["fonts"][fcfg["slug"]] = {
            "name": fcfg["name"],
            "slug": fcfg["slug"],
            "configPath": "{}/fonts/{}/font.json".format(
                cfg["host"], fcfg["slug"]
            )
        }

        if "license" in fcfg:
            generated_cfg["fonts"][fcfg["slug"]]["licensePath"] = "{}/fonts/{}/LICENSE".format(cfg["host"], fcfg["slug"])
    
    return generated_cfg

FONT_CONFIGS = {}
def fetch_font_map(font_slug):
    global FONT_CONFIGS
    # Check cache for font config
    if font_slug not in FONT_CONFIGS.keys():
        # Cache font configs.
        FONT_CONFIGS[font_slug] = generate_font_map(font_slug)
    
    return FONT_CONFIGS[font_slug]

FONT_PATHS = {}
def fetch_font_path(font_slug):
    global FONT_PATHS
    if len(FONT_PATHS) <= 0:
        cfg = fetch_raw_config()
        for font_name in cfg["fonts"]:
            for path in cfg["font_paths"]:
                if os.path.isdir(os.path.join(path, font_name)):
                    font_path = os.path.join(path, font_name)
                    with open(os.path.join(font_path, 'font.yaml')) as fcf:
                        fcfg = yaml.load(fcf, Loader=yaml.FullLoader)
                        FONT_PATHS[fcfg['slug']] = font_path

    if font_slug not in FONT_PATHS.keys():
        return None

    return FONT_PATHS[font_slug]

def generate_font_map(font_slug, include_raw=False):
    """
    Generate a font config based on font.yaml
    with the following properties:

    ```
    name
    slug
    author
    licenseType
    members:
    - <member-slug>:
        name
        slug
        style (default: normal)
        weight
        ttf
    ```
    """

    if include_raw:
        cfg = generate_config()
    else:
        cfg = fetch_config()
    font_path = fetch_font_path(font_slug)

    if not font_path:
        return None
        
    with open(os.path.join(font_path, 'font.yaml')) as fcf:
        fcfg = yaml.load(fcf, Loader=yaml.FullLoader)
        
    generated_cfg = {
        "name": fcfg["name"],
        "slug": fcfg["slug"],
        "author": fcfg["author"],
        "licenseType": fcfg["license_type"],
        "members": {}
    }

    if include_raw:
        generated_cfg["rawFontPath"] = font_path

    for member in fcfg["members"]:
        generated_cfg["members"][member["slug"]] = {
            "name": member["name"],
            "slug": member["slug"],
            "style": "normal" if "style" not in member else member["style"],
            "weight": member["weight"],
            "ttf": os.path.join("{}/fonts/{}/static/{}.ttf".format(
                cfg["host"],
                fcfg["slug"],
                member["slug"]
            ))
        }
        if include_raw:
            generated_cfg["members"][member["slug"]]["raw_ttf"] = member["ttf"]


    return generated_cfg

def form_font_face(app_host, font_cfg, member_slug):
    """
    Based on a certain font config (see generate_font_map)
    and app host, return a @font-face CSS rule.
    """

    if member_slug not in font_cfg["members"]:
        raise Exception("form_font_face: member {} not found".format(member_slug))

    font_member = font_cfg["members"][member_slug]

    return """@font-face {{
    font-family: {};
    font-style: {};
    font-weight: {};
    src: local("{}"),
         local("{}"),
         url("{}") format("truetype");
}}""".format(
    dquote_long_names(font_cfg["name"]),
    font_member["style"],
    font_member["weight"],
    font_cfg["slug"] + "-" + font_member["slug"],
    font_cfg["name"] + " " + font_member["name"],
    "{}/fonts/{}/static/{}.ttf".format(
        app_host,
        font_cfg["slug"],
        font_member["slug"]
    )
)

def dquote_long_names(name):
    """
    Returns double-quotes if space in string.
    """
    return '"{}"'.format(name) if " " in name else name