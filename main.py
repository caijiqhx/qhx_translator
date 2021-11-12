import sys, getopt

import Translator
from Clipboard import Clipboard
from Translator import translate
from ColorPrint import *

# def parse_opt()


if __name__ == '__main__':
    # try:
    opts, args = getopt.getopt(sys.argv[1:], "hd", ["proxy=", "help"])
    # except getopt.GetoptError:
    #     ColorPrint.print_fail("opt parse error, use -h/--help show usage")
    # TODO: add more opt support
    for opt, arg in opts:
        if opt == "--proxy":
            Translator.proxy = arg

    clipboard = Clipboard(on_update=translate, trigger_at_start=True)
    clipboard.listen()
