#!/usr/bin/env python3

"""
Author: Ville Kumpulainen

MIT License:
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This program scans through a mbox file containing emails and attempts to build
a summary of recruitment messages.
"""

import os, sys, re
sys.path.insert(0, "/home/ville/code/pymailscanner")
from pymailscanner import *

class Main:

    def __init__(self):
        self.reader = EmailReader()
        self.parser = EmailParser()
        self.writer = EmailWriter()

        self.mboxfile = self.reader.read_in(sys.argv[1])

        self.messages = {}
        self.titles = {}
        self.dls = {}

        self.tag_regex = r"\[athene-yrityssuhteet\]|\[atalent recruiting\]|avoin työpaikka|re:"
        self.filler_regex = r"opiskeli\w*|mahdol\w*|kiinnost\w*|työmahdoll\w*|työpaikk\w*|rekrytoint\w*|kaks\w*"
        self.symbol_regex = r"^(:|,|\?)"

        if self.parser.parse_messages(self.mboxfile):
            self.messages = self.parser.get_messages()
            self.titles = self.parser.get_titles()
        else:
            print("Couldn't load messages")
            mboxfile.close()
            sys.exit()

        # Close the mbox file after reading in the data
        self.mboxfile.close()

    def get_deadline(self, string):

        # Matches for "dl", "appl*" and "deadline"
        dl_regex = r"(dl|appl\w*\b|deadline)"

        # Matches for "1.1.", "01.01", "1th" and "asap"
        date_regex = r"((\d{1,2}\.\d{1,2}\.)|(\d{1,2}(st|nd|rd|th)))|(asap?)"

        # Perform searches for both regular expressions against the same string
        re1_match = self.parser.scan_message(string, dl_regex)
        re2_match = self.parser.scan_message(string, date_regex)

        # If both match, it's the one
        if re1_match == re2_match:
            return self.parser.format_date(re1_match)

        # If the deadline-row in the email contains asap, that's probably the application deadline
        elif "asap" in re1_match.lower():
            return "ASAP"

        # If the date row contains "dl" or "deadline", it's probably the application deadline
        elif "dl" in re2_match.lower() or "deadline" in re2_match.lower():
            return self.parser.format_date(re2_match)

        # if still no match, do a cross search to each other's results
        else:
            if re.search(dl_regex, re2_match):
                return self.parser.format_date(re2_match)
            elif re.search(date_regex, re1_match):
                return self.parser.format_date(re1_match)

        # Finally admit defeat
        return "Couldn't find deadline"


    def main(self):

        # Create all the tldr lines and save them to a variable for later
        lines = ""
        for i in self.messages.keys():
            self.titles[i] = self.parser.strip_string(self.titles[i], self.tag_regex, self.filler_regex, self.symbol_regex)
            if not self.titles[i]:
                self.titles[i] = "Deleted whole subjectline"
            lines += self.parser.create_line(i+1, self.titles[i], "DL: " + self.get_deadline(self.messages[i]))

        # Create an empty file to write the message to
        filename = self.writer.create_new_msg()

        # Write the tldr section to the file
        written_chars = self.writer.write_to_file(filename, lines)
        #print("Wrote " + str(written_chars) + " characters to file: " + filename)

        # Append the message bodies to the file
        for key in self.messages.keys():
            self.writer.write_to_file(filename, "\n------\n" + lines.splitlines()[key] + "\n\n")
            self.writer.write_to_file(filename, self.messages[key])

            # Converting the mbox file to plain text leaves * -signs all over the file. Remove them.
            with open(filename, "r") as infile:
                with open(filename + ".new", "w+") as outfile:
                    data = infile.read()
                    data = data.replace("*", "")
                    outfile.write(data)

        # Clean up
        date = filename.replace(".txt", "").replace("msg-", "")
        os.remove(filename)
        os.rename(filename + ".new", "messages-" + date + ".txt")

        # Debug data, if something wasn't written
        if self.parser.skipped_bodies:
            print("\nSkipped " + str(len(self.parser.skipped_bodies)) + " bodies, please check them manually.")
            print(self.parser.skipped_bodies)
        if self.parser.skipped_titles:
            print("\nMissing " + str(len(self.parser.skipped_titles)) + " title(s), please check them manually.")
            print(self.parser.skipped_titles)

if __name__ == "__main__":
    Main().main()
