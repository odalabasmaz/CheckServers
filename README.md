CheckServers  v1.0
==================
This program allows you to check your servers' statuses on WebLogic Application Servers
Informs you by sending e-mails if there is something unusual,
so you do not have to worry about the servers running and check them all the time.

Program scans;
-   running server status under 'Environment > Servers > Configuration' and checks if any state is not RUNNING and/or Health is not OK
-   System status / Health of Running Servers and checks if there is any state rather than OK.


Please, feel free to ask anything.

Orhun Dalabasmaz</br>
odalabasmaz@gmail.com


TESTED ON
---------
- WebLogic Server Version: 12.1.3.0.0
- Gmail and MS Exchange Server SMTP Servers


HOW TO USE
---------
1-  Main python file is **CheckServers.py**</br>

    $ python CheckServers.py
    $ python CheckServers.py onFailOnly=False

    *onFailOnly* parameter is *True* by default.
    You can change it to *False* if you want to inform you even if everything is OK with servers.
    If you let it True, it only informs you in case of an unusual server situation.

2-  Modify **config/WLConfig.py** in order to connect WebLogic Application Server

3-  Modify **config/MailConfig.py** in order to manage your e-mail account, and receivers.

4-  Modify your **crontab** and add new jobs in order to run **CheckServers.py** periodically.

    # Crontab on Linux
    $ export EDITOR=vim     # you can choose your best editor
    $ crontab -e

    # add these lines in
    # send when only failure, checks the statuses in every 5 minutes
    */5 * * * * python /your/path/CheckServers/CheckServers.py
    # send information periodically (every day at 9am, 1pm, 5pm, 9pm)
    0 9,13,17,21 * * * python /your/path/CheckServers/CheckServers.py onFailOnly=False
