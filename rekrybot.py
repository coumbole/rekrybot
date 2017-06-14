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

import os, sys
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

        if self.parser.parse_messages(self.mboxfile):
            self.messages = self.parser.get_messages()
            self.titles = self.parser.get_titles()
        else:
            print("Couldn't load messages")
            mboxfile.close()
            sys.exit()

        # Close the mbox file after reading in the data
        self.mboxfile.close()


    def main(self):

        
                # Create all the tldr lines and save them to a variable for later
        lines = ""
        for i in messages.keys():
            lines += self.parser.create_line(i+1, titles[i])

        # Create an empty file to write the message to
        filename = self.writer.create_new_msg()

        # Write the tldr section to the file
        written_chars = self.writer.write_to_file(filename, lines)
        print("Wrote " + str(written_chars) + " characters to file: " + filename)

        # Append the message bodies to the file
        for key in messages.keys():
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
