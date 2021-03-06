#!/usr/bin/python
"""
hexview.py - hex dump of any file

based on: "Tutorial: Making your own Hex Dump Program" by DrapsTV
https://www.youtube.com/watch?v=B8nRrw_M_nk&index=1&list=WL

"""
import argparse
import os


ASCII = 'ascii'
CTRL = 'ctrl'
OTHER = 'other'


COLORS = {
    "black": '\33[30m',
    "white": '\33[37m',
    "red": '\33[31m',
    "green": '\33[32m',
    "yellow": '\33[33m',
    "blue": '\33[34m',
    "magenta": '\33[35m',
    "cyan": '\33[36m',
    "grey": '\33[90m',
    "lightgrey": '\33[37m',
    "lightblue": '\33[94m'
}


def char_type(c):
    if ord(c) < 128 and ord(c) > 32:
        return ASCII
    if ord(c) <= 16:
        return CTRL
    return OTHER


def make_color(c):
    """
    Formats color for byte depends on if it's printable ASCII
    """
    # printable ASCII:
    if char_type(c) == ASCII:
        retval = "{}{:02X}{}".format(COLORS['green'], ord(c), COLORS['white'])
    if char_type(c) == OTHER:
        retval = "{}{:02X}{}".format(COLORS['yellow'], ord(c), COLORS['white'])
    if char_type(c) == CTRL:
        retval = "{}{:02X}{}".format(COLORS['red'], ord(c), COLORS['white'])
    return retval


def format_text(c):
    """
    Formats color for character depends on if it's printable ASCII
    """
    if char_type(c) == ASCII:
        retval = "{}{}{}".format(COLORS['lightblue'], c, COLORS['white'])
    if char_type(c) == CTRL:
        retval = "{}.{}".format(COLORS['red'], COLORS['white'])
    if char_type(c) == OTHER:
        retval = "{}.{}".format(COLORS['yellow'], COLORS['white'])
    return retval


def format_chunk(chunk, start, stop, dec=False):
    """
    Formats one full chunk (byte)
    """
    if dec:
        return " ".join("{}:{}{:#04}{} ".format(make_color(c), COLORS['grey'],
                                                ord(c), COLORS['white']) for c in chunk[start:stop])
    else:
        return " ".join("{} ".format(make_color(c)) for c in chunk[start:stop])


def extract_shellcode(start, end, read_binary):
    read_binary.seek(start)
    shellcode = ""
    s = read_binary.read(end - start)
    for c in s:
        if ord(c) == 0:
            shellcode = shellcode + "{}".format(COLORS['red']) + str(
                hex(ord(c))).replace("0x", "\\x") + "{}".format(COLORS['white'])
        else:
            shellcode = shellcode + "{}".format(COLORS['yellow']) + str(
                hex(ord(c))).replace("0x", "\\x") + "{}".format(COLORS['white'])
    print "\n{}[+] Shellcode extracted from byte(s) {:#08x} to {:#08x}:{}".format(COLORS['cyan'], start, end, COLORS['white'])
    print "\n{}\n".format(shellcode)


def main():
    """
    main program routine
    """
    __FROM = 0
    __TO = 0

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Specify a file")
    parser.add_argument(
        "-d", "--decimal", help="Display DEC values with HEX", action="store_true")
    parser.add_argument(
        "-s", "--start", help="Start byte")
    parser.add_argument(
        "-e", "--end", help="End byte")
    parser.add_argument(
        "-S", "--shellcode", help="Extract shellcode (-s and -e has to be passed)", action="store_true")

    args = parser.parse_args()
    b = 16

    if args.file:
        with open(args.file, 'rb') as infile:
            if args.start > -1 and args.end and (int(args.start, 16) > -1 and int(args.end, 16) > int(args.start, 16)):
                __FROM = int(args.start, 16)
                __TO = int(args.end, 16)
            else:
                __TO = os.path.getsize(args.file)

            if args.shellcode and __FROM > -1 and __TO:
                extract_shellcode(__FROM, __TO, infile)

            infile.seek(__FROM)
            offset = __FROM
            
            print "{}[+] File content: {}\n".format(COLORS['cyan'], COLORS['white'])
            while offset < __TO:
                chunk = infile.read(b)
                if len(chunk) == 0:
                    break

                text = str(chunk)
                text = ''.join([format_text(i) for i in text])

                output = "{}{:#08x}{}".format(
                    COLORS['cyan'], offset, COLORS['white']) + ": "

                output += format_chunk(chunk, 0, 4, args.decimal)
                output += " | "
                output += format_chunk(chunk, 4, 8, args.decimal)
                output += " | "
                output += format_chunk(chunk, 8, 12, args.decimal)
                output += " | "
                output += format_chunk(chunk, 12, 16, args.decimal)

                if len(chunk) % b != 0:
                    if args.decimal:
                        output += "   " * (((b * 2) - 4 - len(chunk))) + text
                    else:
                        output += "   " * (b + 4 - len(chunk)) + text
                else:
                    output += " " + text

                print output
                offset += 16

            print
    else:
        print parser.usage


if __name__ == "__main__":
    main()
