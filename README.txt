bot: gubbins-ng.py
author: birchy (support@bespokebots.com)
python version: 3.2.3 (compatible with Python 2.7+)

-- PRE-REQUISITES --
Betfair have increased security and you can no longer login from a bot using only
your username and password. You will now require an ssl certificate which is
linked to your account. This will be sent along with your username and password.
The api-ng library will handle this automatically as long as you have met the
following requirements.

Before running this bot you MUST:

1. Create ssl keys and put them in the betfair/ssl_keys folder. More info at:
https://api.developer.betfair.com/services/webapps/docs/display/1smk3cen4v3lu3yomq5qye0ni/Non-Interactive+%28bot%29+login
If the above url doesn't work, go to the api docs page and search for "Non-Interactive login"
If you are a Linux user, I have written a tutorial here:
http://diybetfairbots.lefora.com/topic/19400982/Debian-Linux-Creating-an-SSL-certificate-for-login
You will have to join the forum to read it.

NOTE: default cert names are prefixed 'client-2048'. To use the bespokebots API-NG
library, you must rename these files to your betfair account username,
e.g. 'yourusername.crt' and 'yourusername.key'. This makes it easy to identify
which account the certs are linked to, particularly if you have mulitiple betfair
accounts. See api_ng.py __init__() function for more info. The included bot also
assumes this naming convention - see run() function, ssl_prefix for more info.

2. Create an application key:
https://api.developer.betfair.com/services/webapps/docs/display/1smk3cen4v3lu3yomq5qye0ni/Application+Keys

3. Enter your account details in manager.py. HINT: APP_KEY should be your LIVE
data application key and NOT the delayed one.

4. You will need to install the Python "http requests" library:
http://docs.python-requests.org/en/latest/user/install/#install
For Linux users, this will require the following commands:
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python get-pip.py
$ sudo pip install requests


-- RUNNING THE BOT ---
The parent is manager.py and automates bot startup and error handling. It keeps
the bot running 24/7 and is intended for use on dedicated or VPS servers and
supports a "start it and forget it" ethic. You can also run the bot on your own
pc - it works in exactly the same way. There is a variable named EXIT_ON_ERROR
which tells the bot whether to run forever (logging errors to err_log.txt) OR
exit when an error occurs. This is currently set to True, so the bot will exit
when an error occurs. Once you have the bot working how you want, you should set
this to False - the bot will then run 24/7 and log any errors to err_log.txt.
If an error occurs,the bot will wait for 60 seconds and then restart automatically.
HTTP errors are fairly common - this is not a fault within the bot and are due to
Betfair's servers being unreachable/overloaded/slow responding/etc. Also, the
nature of the internet means we can never guarantee 100% uptime as your own
connection may occasionally suffer from lag, packet loss, disconnections, etc.

Assuming you have Python 2.7+ installed, created your ssl certificates, uploaded
them to your betfair account, copied the certs to the betfair/ssl_certs folder,
created your application key and entered it into manager.py along with your
username and password...you are ready to start botting!

First, you need to get the full path to the manager.py file. On Linux, this will
be something like:
"gubbins-ng/manager.py" (if you unzipped the download to your HOME folder)
On Windows this may be:
"C:\Users\burt\Desktop\gubbins-ng\manager.py" (if your Windows username is "burt"
and you unzipped the download to your desktop)

To run the bot in a command terminal, simply open a command prompt and enter:
"python gubbins-ng/manager.py" (or whatever your file path is).

You can also run the bot from your favourite Python editor/IDE if it has launch
capabilities. And on Windows, I believe double-clicking the manager.py file will
also launch the bot in a DOS terminal if you have Python installed correctly...
although this is unverified as I do not have a Windows machine.

Note that there is NO Graphical User Interface (GUI) with this bot as it is not
intended for human interaction. If you need a GUI, you will have to write your
own. This api-ng library and test bot are just a building block
to get you started. The rest is up to you. ;o)

GOOD LUCK!
