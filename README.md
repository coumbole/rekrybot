# Rekrybot

Uses the [mailscanner](https://github.com/coumbole/mailscanner) library
to read recruitment messages from an IMAP mailbox and compiles them into
a single summary email message.

### Contents

- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)


### Important notes

Rekrybot is especially optimized for aTalent Recruiting's messages.
However, it should be able to figure out other generic messages as well.

For now, e.g. adding more filters for parsing the subject line etc. is a
little bit labourious and requires you to know something about regex and
python. In the future there could be a browser based UI.

## Usage

In order to use Rekrybot yourself, you need to complete the following
tasks.


- [Installation](#installation)
- [Setup email](#setup-email)
- [Update configurations](#update-configurations)
- [Running Rekrybot](#running-rekrybot)
- [Aftercare](#aftercare)


#### Installation

Install prerequisities
- Python 3.4+
- Git

For customization / development
- Text editor of choice
- Virtualenv


To install, run the following:
``` bash
cd && git clone https://github.com/coumbole/rekrybot.git && cd rekrybot

# Optionally at this point, before installing dependencies
virtualenv -p python3 .
source bin/activate

# Install the dependency
pip install -r requirements.txt
```

#### Setup email

You must create a new mailbox called "Recruitment" (without the quotes),
and add some messages there.


#### Update configurations

Open .rekrybotrc with your favourite text editor and update the
credentials.

`vim .rekrybotrc`

Hostname is the IMAP server's hostname. For example in my case, I'm
using my Aalto university provided email, so my hostname is
`mail.aalto.fi`

The other fields should be self-explanatory.

Once the data is updated, move it to your home directory.

`mv .rekrybotrc ~/`


#### Running rekrybot

Now you're ready to start using rekrybot. Make sure you've got the
Recruitment mailbox (folder) set up, some messages in there.

Now simply run `./rekrybot.py` and check your email. You should have a
new draft compiled from all the emails in Recruitment folder.

You can now go ahead an delete the contents of Recruitment folder.
Rekrybot doesn't delete any messages at all just to be safe, but it
copies the used messages to a timestamped archive folder.


#### Aftercare

Rekrybot is far from finished. It's possible that it was not able to
figure out all the deadlines, or it could've deleted the whole subject
line. Fixing these is left to you, but it probably still managed to do
most of the manual copy-pasting.


#### Contributing

If you have any problems or improvement ideas, please open an issue. If
you want to contribute, pull requests are welcome but please ask first
to make sure the feature / fix is not already on the way.


#### License

Rekrybot is licensed under the GNU GPLv3.


#### About operating systems

Works at least in Linux, should work out of the box in MacOS, no idea
about windows.
