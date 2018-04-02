# CMU CS Bot
Chat Bot for the CMU CS Discord Server

# Installation

``git clone https://github.com/coloradomesa/discord-cs-bot``

``pip install -r requirements.txt``

Then just run it with your api token: 

``DISCORD_API_TOKEN=<token> python3 -m discord-cs-bot/csms_bot.py``


#### On startup the bot will output the ID's of the roles of every server it can see, be sure to copy the ID's for the student/alumni roles into an environment variable like so:

``DISCORD_API_TOKEN=<token> CSMS_DISCORD_STUDENT_ROLE_ID=<student role id> CSMS_DISCORD_ALUMNI_ROLE_ID=<alumni role id> python3 -m disocrd-cs-bot/csms_bot.py``

Soon, I will have a docker container defined in a dockerfile in this repo. 

Until then, you can make one yourself based on the python image in the docker hub library.
Example:

```dockerfile
FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python3 csms_bot.py
```
