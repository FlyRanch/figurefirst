import os
import errno
import sys
import shutil
import logging
from argparse import ArgumentParser

from .constants import PACKAGE_DIR

logger = logging.getLogger(__name__)


def mkdir_p(path):
    """https://stackoverflow.com/a/600612/2700168"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def copy_extensions(src_dir, tgt_dir):
    for root, _, fnames in os.walk(src_dir):
        for fname in fnames:
            if not (fname.endswith('.py') or fname.endswith('.inx')):
                continue

            src_fpath = os.path.join(root, fname)
            logger.info("Copying {} into directory {}".format(src_fpath, tgt_dir))
            shutil.copy2(src_fpath, tgt_dir)


def main():
    parser = ArgumentParser(description="Copy inkscape extensions to desired directory")
    parser.add_argument(
        "target_dir", default=None, help="Inkscape extension directory. On unix, this will probably be\n"
        "~/.config/inkscape/extensions\n"
        "On Windows, this will probably be\n"
        "C:\\Program Files\\Inkscape\\share\\extensions"
    )

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)

    tgt_dir = args.target_dir
    mkdir_p(tgt_dir)

    src_dir = os.path.join(sys.prefix, 'inkscape_extensions')

    copy_extensions(src_dir, tgt_dir)


if __name__ == '__main__':
    main()
