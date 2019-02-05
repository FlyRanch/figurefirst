from __future__ import print_function

import os
import sys
import shutil
import logging
from argparse import ArgumentParser

try:
    input = raw_input
except NameError:
    pass

logger = logging.getLogger(__name__)


overwrite_prompt = """
Target extension file {} already exists. Overwrite? (enter number, press return)
  1. Yes
  2. No
  3. All
  4. None
  
"""


def get_overwrite_input(tgt):
    while True:
        val = input(overwrite_prompt.format(tgt))
        try:
            val = int(val)
        except ValueError:
            print("Unrecognised input '{}'".format(val))
            continue
        if not 1 <= val <= 4:
            print("Illegal value {}".format(val))
        return [None, "yes", "no", "all", "none"][val]


def copy_extensions(src_dir, tgt_dir, overwrite_all=False, overwrite_none=False):
    for root, _, fnames in os.walk(src_dir):
        for fname in fnames:
            if not (fname.endswith('.py') or fname.endswith('.inx')):
                continue

            src_fpath = os.path.join(root, fname)
            tgt_fpath = os.path.join(tgt_dir, fname)

            copy_this = True

            if os.path.isfile(tgt_fpath):
                if overwrite_all:
                    os.remove(tgt_fpath)
                elif overwrite_none:
                    copy_this = False
                else:
                    overwrite_input = get_overwrite_input(tgt_fpath)
                    if overwrite_input == "all":
                        overwrite_all = True
                        overwrite_input = "yes"
                    elif overwrite_input == "none":
                        overwrite_none = True
                        overwrite_input = "no"

                    if overwrite_input == "yes":
                        os.remove(tgt_fpath)
                    elif overwrite_input == "no":
                        copy_this = False

            if copy_this:
                logger.info("Copying {} into directory {}".format(src_fpath, tgt_dir))
                shutil.copy2(src_fpath, tgt_fpath)


def get_default_target():
    if sys.platform.startswith("win32"):
        return os.path.join("c:", "Program Files", "Inkscape", "share", "extensions")
    elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        return os.path.expanduser(os.path.join("~", ".config", "inkscape", "extensions"))


def main():
    parser = ArgumentParser(description="Copy inkscape extensions to desired directory")
    parser.add_argument(
        "target_dir", default=get_default_target(), nargs="?",
        help="Inkscape extension directory. On linux and macos, defaults to\n"
        "~/.config/inkscape/extensions ; "
        "On Windows, defaults to "
        "C:\\Program Files\\Inkscape\\share\\extensions"
    )
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite extensions of the same name without asking")
    parser.add_argument("-e", "--ease", action="store_true", help="Do not overwrite existing extensions")

    try:
        args = parser.parse_args()
        if args.target_dir is None:
            raise ValueError("\nInstall failed: Could not infer inkscape extension directory. "
                             "Please give it explicitly.\n")

        tgt_dir = os.path.expanduser(os.path.expandvars(args.target_dir))

        if not os.path.isdir(tgt_dir):
            raise ValueError("\nInstall failed: Directory {} does not exist. ".format(args.target_dir) +
                  "Ensure Inkscape is installed correctly, and/or give the extension directory explicitly.\n")

        src_dir = os.path.join(sys.prefix, 'inkscape_extensions')

        if args.force and args.ease:
            args.force = False
            args.ease = False

        copy_extensions(src_dir, tgt_dir, args.force, args.ease)
    except Exception as e:
        parser.print_help()
        raise e


if __name__ == '__main__':
    main()
