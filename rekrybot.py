#!/usr/bin/env python3

"""
Author: Ville Kumpulainen 2017
License: GNU GPL v3.0
"""

import os
import re
import time
import imaplib
import datetime
import mailscanner
import configparser
from email.message import EmailMessage

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
        self.whitespacechars = r"(\n|\r|\t)"
        self.tag_regex = r"\[.*\]|avoin työpaikka|re:"
        self.filler_regex = r"valmistu\w*|opiskeli\w*|mahdol\w*|" +\
            r"loppuv\w*|miele\w*|kiinnost\w*|kiinos\w*|upe\w*|työmahdoll\w*" +\
            r"|työpaikk\w*|rekrytoint\w*|usei\w*|kaks\w*|\w*paik\w*"
        self.symbol_regex = r"^(:|,|\?)|(/)"
        self.start = r"hei.*$|moi.*$"
        self.end = r"(^[-]{3,})"

    def get_deadline(self, string):
        """Attempts to find a deadline from string."""

        # Matches for "dl", "appl*" and "deadline"
        dl_regex = r"(dl|appl\w*\b|deadline)"

        # Matches for "1.1.", "01.01", "1th" and "asap"
        date_regex = r"((\d{1,2}\.\d{1,2}\.)|(\d{1,2}(st|nd|rd|th)))|(asap?)"

        # Tries to find a line from the message that contains words
        # "dl", "apply" or "deadline"
        re1_match = self.parser.scan_message(string, dl_regex)

        # Tries to find a line from the message that contains a date.
        re2_match = self.parser.scan_message(string, date_regex)


        # If a single line contains something about a deadline and a
        # date, it's probably the deadline date
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
        """This executes the things described in the class description.

        First of all, Rekrybot loops through all found messages, and
        tries to form a summary line about the job posting, such as:

        2: Company name: Some junior position - DL: 15.11.

        It appends these to the beginning of the newsletter, followed by
        all the message bodies of the individual recruitment messages.

        Finally, it creates a blank email message, sets it header data
        accordingly (subject, sender, recipient) and appends the
        previously created content to the message body.
        """

        body = ""
        lines = ""
        contents = ""

        # Index is for tl;dr numbering, thus starting from 1
        index = 1

        # Go through each item in messages and append to mail body
        for i in self.messages:

            # Mail subject
            subject_line = self.parser.strip_string(
                i[0],
                self.whitespacechars,
                self.tag_regex,
                self.filler_regex,
                self.symbol_regex)

            if not subject_line:
                subject_line = "Deleted whole subjectline"

            # Form the summary line
            line = self.parser.create_line(index,
                                           subject_line,
                                           "DL: " + self.get_deadline(i[1]))

            lines += line


            # Append a recruitment message's body to the contents with
            # the oneliner in the beginning and some whitespace in the end
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

        # Note to user: You can now delete all messages in the
        # Recruitment mailbox. This program does not delete anything,
        # just in case. If no errors arose, copies of the
        # messages exist in Recruitment/archive/date submailbox.

if __name__ == "__main__":
    Main().main()
