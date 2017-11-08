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

import configparser
import datetime
from email.message import EmailMessage
import imaplib
import os
import re
import sys
import time
import mailscanner

class Main:
    """Combines a bunch of email message into single newsletter.

    Reads in all messages from Recruitment folder, creates a TL;DR
    section from them and adds the message bodies in the end
    """

    def __init__(self):

        # Config file is expected to be at ~/.rekrybotrc
        self.config_path = os.path.expanduser('~/.rekrybotrc')

        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.reader = mailscanner.ImapReader(self.config)

        self.parser = mailscanner.Parser()


        # Initialize IMAP connection
        self.connection = self.reader.open_connection()

        # List of subject-body tuples
        self.messages = self.reader.fetch_all_messages(
            self.connection,
            'Recruitment',
            True)

        # Regular expressions used in filtering  messages
        self.newline = r"\n"
        self.tag_regex = r"\[athene-yrityssuhteet\]|\[atalent recruiting\]|avoin työpaikka|re:"
        self.filler_regex = r"valmistu\w*|opiskeli\w*|mahdol\w*|" +\
            r"loppuv\w*|miele\w*|kiinnost\w*|työmahdoll\w*" +\
            r"|työpaikk\w*|rekrytoint\w*|kaks\w*|\w*paik\w*"
        self.symbol_regex = r"^(:|,|\?)|(/)"
        self.start = r"hei.*$|moi.*$"
        self.end = r"(^[-]{3,})"

    def get_deadline(self, string):
        """Attempts to find a deadline from string."""

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
        """This executes everything described in module docstring."""

        # Full message body
        body = ""

        # TL;DR lines
        lines = ""

        # The recruitment message
        contents = ""

        # Index is for tl;dr numbering
        index = 1

        # Go through each item in messages and append to mail body
        for i in self.messages:

            ################
            # Mail subject #
            ################

            subject_line = self.parser.strip_string(
                i[0],
                self.newline,
                self.tag_regex,
                self.filler_regex,
                self.symbol_regex)

            if not subject_line:
                subject_line = "Deleted whole subjectline"

            # Form the Tl;DR line
            line = self.parser.create_line(index,
                                           subject_line,
                                           "DL: " + self.get_deadline(i[1]))
            lines += line

            #############
            # Mail body #
            #############

            # Append the recruitment message body to contents
            contents += line + "\n\n" + i[1] + "\n\n\n\n----\n"

            # Increment index by one and start over
            index += 1

        # Form the email body
        body += lines + "\n\n-----\n" + contents

        # Initialize a new message
        msg = EmailMessage()

        # Set email header
        msg['Subject'] = 'Recruitment mail'
        msg['From'] = 'rekrybot@athene.fi'
        msg['To'] = 'rekry@athene.fi'

        # Append TL;DR:
        msg.set_content(body)

        # Append the message to drafts
        self.connection.append('Drafts', '',
                               imaplib.Time2Internaldate(time.time()),
                               str(msg).encode('UTF-8'))

        # Select all messages in recruitment
        typ, [response] = self.connection.search(None, 'All')

        # If something goes wrong, abort mission
        if typ != 'OK':
            raise RuntimeError(response)

        msg_ids = ','.join(response.decode('utf-8').split(' '))

        # Create a timestamp for archive creation
        timestamp = datetime.date.today().isoformat()

        # Create a new arhive mailbox for the messages
        mailboxname = 'Recruitment/archive/' + timestamp
        typ, response = self.connection.create(mailboxname)

        # Copy the messages over to the archive
        self.connection.copy(msg_ids, mailboxname)

        # Close connection, we're done here
        self.connection.close()

if __name__ == "__main__":
    Main().main()
