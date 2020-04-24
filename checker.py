import yaml
import os
import sys
import contextlib

def check():
    """
    Checks that the current Fontiles directory is configured
    correctly, that all font families are present and have no
    missing files, etc. It prints out the current
    configuration upon success.
    """

    has_error = False

    # Ensure that fonts.yaml exists
    if not ensure_file_exists("app.yaml"):
        print("ERROR: app.yaml configuration file missing. Aborting.")
        sys.exit(1)

    with open("app.yaml") as cf:
        cfg = yaml.load(cf, Loader=yaml.FullLoader)

    # Ensure that config is a dictionary
    if type(cfg) is not dict:
        print("ERROR: app.yaml was not properly parsable as a dictionary. Aborting.")
        sys.exit(1)
    
    # Ensure that members of the config are here.
    cfg_required_keys = {'name', 'host', 'font_paths', 'fonts'}
    if not cfg.keys() >= cfg_required_keys:
        print("ERROR: Essential keys in app.yaml missing: {}. Aborting.".format(cfg_required_keys - cfg.keys()))
        sys.exit(1)

    # Otherwise, print out a summary of the file.
    print("""
CONFIGURATION (app.yaml)
App Name:\t{}
Host:    \t{}
URL Test:\t{}

FONT PATHS ({} defined):
{}

# OF FONTS:\t{}
""".format(
        cfg['name'], cfg['host'],
        "{}/ping".format(cfg['host']),
        len(cfg['font_paths']),
        "\n".join(cfg['font_paths']),
        len(cfg['fonts'])
    ))

    # Check duplicates of fonts and font paths
    if len(set(cfg['font_paths'])) < len(cfg['font_paths']):
        print("WARNING: Checker found duplicate font paths listed.\n")

    if len(set(cfg['fonts'])) < len(cfg['fonts']):
        print("WARNING: Checker found duplicate fonts listed.\n")
    

    # Now that a configuration has been found,
    # it's time to investigate that each font
    # is located properly.
    for font in cfg['fonts']:
        has_error = not check_font(font, cfg['font_paths']) or has_error

    if has_error:
        print("Checker found issues. Check logs above for errors/warnings.")
        sys.exit(1)

    print("Checker ran successfully without finding errors.")
    return True


def check_font(font_name, font_paths):
    def ret_error(msg=None):
        print("(ERROR)")
        print("    \\__ ERROR: {}".format(msg)) if msg else None
        print("  \\__ check ended with error!!\n")
        return False

    def ret_warnings(msgs=[]):
        print("(WARNING)")
        for msg in msgs:
            print("    \\__ WARNING: " + msg)
        print("  \\__ check ended with warnings, see above.\n")
        return False

    print("Checking font '{}':".format(font_name))

    # Locate the font among paths
    print("  \\__ check 1: locate font folder ", end="")
    font_path = None
    for path in font_paths:
        if os.path.isdir(os.path.join(path, font_name)):
            font_path = os.path.join(path, font_name)

    if not font_path:
        return ret_error()
    print("(pass)")
    
    # Quickly check that font.yaml is defined
    print("  \\__ check 2: locate font.yaml ", end="")
    if not ensure_file_exists(os.path.join(font_path, 'font.yaml'), True):
        return ret_error()
    print("(pass)")

    # Validate that keys are present
    print("  \\__ check 3: validate font.yaml ", end="")
    with open(os.path.join(font_path, 'font.yaml')) as cf:
        cfg = yaml.load(cf, Loader=yaml.FullLoader)

    # Ensure that config is a dictionary
    if type(cfg) is not dict:
        return ret_error("font.yaml not properly parsable as dictionary")
    
    # Check that required keys are present
    cfg_required_keys = {'name', 'slug', 'members'}
    if not cfg.keys() >= cfg_required_keys:
        return ret_error("Missing essential keys: {}".format(cfg_required_keys - cfg.keys()))

    warnings = []

    # warning 1: undefined author
    if 'author' not in cfg:
        warnings += ['author tag missing']

    # warning 2: license defined but file not found
    if 'license' in cfg and not ensure_file_exists(os.path.join(font_path, cfg['license'])):
        warnings += ['license file not found']

    # warning 3: license type undefined/unknown
    VALID_LICENSES = ['OFL1.1', 'none']
    if 'license_type' not in cfg or cfg['license_type'] not in VALID_LICENSES:
        warnings += ['invalid/missing license type']
    
    # warning 4: no members in family
    if len(cfg['members']) <= 0:
        warnings += ['no members in family']

    member_names, member_slugs = [], []

    for index, member in enumerate(cfg['members']):
        # warning 5: member has no name
        if 'name' not in member:
            warnings += ['member o' + str(index) + ' of family has no name']
            member['name'] = 'o' + str(index)
        # warning 5.5: member name already exists
        if member['name'] in member_names:
            warnings += ['duplicate member of name ' + member['name']]
            continue
        member_names += [member['name']]
        # warning 6: member has no slug
        if 'slug' not in member:
            warnings += ['member ' + member['name'] + ' has no slug']
            continue
        if member['slug'] in member_slugs:
            warnings += ['duplicate member of slug ' + member['slug']]
            continue
        member_slugs += [member['slug']]
        # warning 7: member has no weight
        if 'weight' not in member:
            warnings += ['member ' + member['name'] + ' has no weight']
        # warning 8: member has no ttf or is not found
        if 'ttf' not in member or not ensure_file_exists(os.path.join(font_path, member['ttf'])):
            warnings += ['member ' + member['name'] + ' does not have ttf (src)']

    # Begin emitting warnings if present
    if warnings:
        return ret_warnings(warnings)

    print("(pass)")
    print("  \\__ check ended OK.\n")

    return True


def ensure_file_exists(filename, is_silent=True):
    """
    Asserts that a file `filename` exists and openable.
    """
    try:
        _ = open(filename)
    except FileNotFoundError:
        if not is_silent:
            print("ERROR: could not read file {}".format(filename))
        return False

    return True

def ensure_check():
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        return check()

if __name__ == "__main__":
    print("Starting checker.py")
    check()