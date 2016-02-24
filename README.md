# Udacity fullstack nanodegree Project 5
February 2016

Prepared by Victor Zaragoza vjzara@gmail.com

This file describes the process of completing the course project described [here][1].

#### IP address and SSH port
* IP address 52.34.191.106
* SSH port 2200

#### Passwords
* logins are not accomplished with passwords
* passwords created using package apg
* password for user grader is provided in comments to reviewer section

#### URL to hosted project
http://ec2-52-34-191-106.us-west-2.compute.amazonaws.com/

#### Software installed
* `ntp` for time sync
* `apache2` for server hosting
* `postgresql-9.3` for application database
* `libapache2-mod-wsgi` for use of wsgi application hosting
* `libpq-dev` and `python-dev` to make required Python libraries available for the catalog application
* `git` for version control
* `python-pip` for virtual hosting environment
* `apg` for creating strong passwords

#### Server configuration changes
* created user grader and added to group sudo
* grader can login with udacity_key.rsa, contents pasted into comments to reviewer section
* remote login as root disabled
* updated, upgraded currently installed packages
* timezone is UTC-0
* ufw (firewall) allows only ports 2200, 80, 123
* added localhost definitions to /etc/hosts
* changed permission of `.git` directory in application code directory to 750 to deny permissions

#### Changes made to application code
These changes necessary for program to run on hosted server
* main programming logic copied from `catalog_app.py` to `__init__.py`
* path to client_secrets json file changed to absolute
* line under `def connect` and `psycopg2.connect` changed to connect as user catalog
* line for `app.run` changed to suit environment

#### References
* Timezones and ntp
https://help.ubuntu.com/community/UbuntuTime#Using_the_Command_Line_.28terminal.29
* firewall
https://help.ubuntu.com/community/UFW
* deploying a flask app and virtual hosting
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
* Fixing sudo error message
http://askubuntu.com/questions/59458/error-message-when-i-run-sudo-unable-to-resolve-host-none
* bash history
http://unix.stackexchange.com/questions/145250/where-is-bashs-history-stored
* transferred an image file from local to server for my website logo
https://www.digitalocean.com/community/tutorials/how-to-use-sftp-to-securely-transfer-files-with-a-remote-server
* creating the db user named catalog with the proper attributes
http://www.postgresql.org/docs/9.3/interactive/sql-createrole.html
* additional args required for psycopg2.connect so that it connects as the catalog db user
https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL#Connect_to_Postgres
* granting table permission to the catalog db user
http://stackoverflow.com/questions/15520361/permission-denied-for-relation
* changing the path of client secrets json file from relative to absolute
https://discussions.udacity.com/t/apache-cant-find-file-in-main-directory/24498
* Making both the IP and the public Amazon EC2 instance URL both point to the app
https://discussions.udacity.com/t/application-shows-with-my-public-ip-address-but-not-with-my-amazon-ec2-instance-public-url/37117
* copying ssh public key to server
https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys
* strong passwords
https://help.ubuntu.com/community/StrongPasswords
* disabling root login
http://manpages.ubuntu.com/manpages/maverick/en/man5/sshd_config.5.html


[1]:https://docs.google.com/document/d/1J0gpbuSlcFa2IQScrTIqI6o3dice-9T7v8EDNjJDfUI/pub?embedded=true

