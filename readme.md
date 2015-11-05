#Restaurant Menu App

## Introduction
This is an app to display restaurant menus. It was created as Project 3 & Project 5 for Udacity's Fullstack Nanodegree.

##Project 5 Notes
### Important info
- IP Address: 54.68.220.44
- SSH Port: 2200
- URL: http://ec2-54-68-220-44.us-west-2.compute.amazonaws.com/
- SSH Key: -----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAraJPljOih9b5rdLv9MqP8FlXGMgkF7KDPUMSZpJXcG+emJhE
mLDYQxXbkWQv++oq3thVtSi5zyVxv/jMf5E1JVlvpCM2gwkXVFBhMfctZnhnMSmB
e2YJZeqsBkX1gdt64nfnzsDyAPI6Irl/TtgGbkZE2mKsNIoBp5GmQv7olgmZVhXY
DpjP3L8HUg19vJOu3krCelrh0GI6UoMQoPAXGtL3jHUXARE31Cu8PgTFnZkFVIMT
t+P89LXPVGEBqGd83bDVh7ScxPcFqXW2RRwZBwzjn+clC0G9YYigy1BrOMDmRTbQ
MIsM5PgzKKvORlBDdDN10DwyIX3KAisehvPjtQIDAQABAoIBAFznbeIWOq6oLev9
43p9L8sQYnPWEsnDMEmFK8FKKBL3Bkrrnjh81xn+Bf+jNbF6t/mIk0NdSR43EMgA
3ZqcHW2gjwWp+a7fHGZ2o6rScK5VWhGJ/cgC7qBjkivBHv2ea//k3FlaD6LF+Kk/
y4hqOfajDpAzH6T0+rGoUueh8Nzl37C8LdlUMEuNJzGP2la0UumAqenviKZkE2rM
1Twv9fcIT7CuxvAq50d0mSu0SiDU5jpAZVc1DLmrvnfccGzoiFtrC3+xpojdNzsZ
LVv9Lw20qd7LkGG2ETT1YtuUuFvqaBt716+d257vxblbBg2kz4Ev2SGlICMQATPX
StFGnIECgYEA4yfH0hJWgIZL4W9esu4MWq90s9/mHIkfMBs5ILAAmBBN3lCG5L0x
fNZmiENvFzBRfzzkf1W0VvcSHXxwsrv1Erfrsw7lVjCZN3ddagx6ubtPL0qNeJQ1
Sdehj9BFfyKIArLlWQEJHJgJDlDen9UaWqahSN0dVpYITIehHCkvlCUCgYEAw66x
Uh5pG4y504BO1b0mB8Mr0+rafeT6G+9rsdIl1xe7WcrqPgMXHcAF/3Tqh3pLx5HL
4AFVp8gM2bFP9SWHrdpYcBXsTQeKjpOgenCIpSQHPQSF5/+uj1ieqT9v3819Jg0G
lTlO5iWh8YMYbMTpeqravYwm8rrWmYdEgOUMtFECgYEAwu9TgopsI1WcbrS1TtYM
UhJ6ExbUka52zkC+cLe5esWbHWp7qHZXrqsLSGqePgcgGRH3gPLalTroF9e/mxLD
iLG/GmVxF9sS0U+lIand89+zX4EaEN0XMexTYGg6C5VlpPNC8HN8D0bFlrx9oCov
uJWAmVfvomuUaaCG+PS7OOUCgYB9F2TFkSkx8mEsgn5jBnqURcDzxNON3V3Bk+kt
kKCeAs7ClQPvRnx1iTaMWoo+twBQgLRq6499JVaJp17s4OP+UHFunaUkjOiXQmo5
O00u/HwgFo8fgwRtIIK0wRfcYvlY5MTLigoU+AOxZ1Oq3KpAv4370+dmDeh31tAE
8eeQMQKBgEYJJnmRiiT3XXPuhEU30PQ0HsQ2cHPKI0dwesGzwcAceRVI264r442v
HJ2Ynod+DvNSNSjNtUfBK0Iy8GgQmTRjl/Q4wzBfXn6HA1zMztn5d5M+Vd2Kz67s
2WRqhFRcyIRNyYynyuomycqmp8aXNDAiasL1qiE0ZaUlhNh5mNk4
-----END RSA PRIVATE KEY-----
###Changes made to server
- Created user grader with password graderPASSWORD
- Gave user grader sudo permissions be creating /etc/sudoers.d/grader
- Updated package list
- Upgraded all packages (except grub because I was afraid to mess with the bootloader)
- Changed SSH port from 22 to 2200 by changing Port entry in /etc/ssh/sshd_config
- Changed UFW permissions to:
  - Deny Incoming By Default
  - Allow Outgoing by Default
  - Allow incoming traffic on 2200, 80, and 123
- Changed timezone to UTC using sudo dpkg-reconfigure tzdata
- Installed apache2
- Install libapache2-mod-wsgi
- Modifed /etc/apache2/sites-enabled/000-default.conf
- Installed python-pip
- Installed git
- Installed postgresql-server-dev-9.3
- Cloned my project repo to /var/www/restaurant_menu
- Used pip to install flask
- Used pip to install oauth2client
- Used pip to install sqlalchemy
- Used pip in install psycopg2
- Installed postgreSQL
- Changed PermitRootLogin in /etc/ssh/sshd_config to no

  ## Installation
  This app was built using Python 2.7.6. If you want to use a different version of Python do so at your own risk.

  1. Install all of the dependencies The easiest way to go about doing this is to install a vagrant virtual machine as described here: [https://www.udacity.com/wiki/ud197/install-vagrant](https://www.udacity.com/wiki/ud197/install-vagrant).

  2. Run database_setup.py to create the proper database schema.

  3. **(OPTIONAL)** Run lotsofmenus.py to populate the database with dummy data.

  4. **(OPTIONAL)** If you want to use your own Google & Facebook account make sure to change the information client_secrets.json and fb_client_secrets.json. You should also change the data-clientid and appId in login.html. You should be able to find them with a text search.

  5. Run project.py, which will start the Flask app and run a local server on port 5000. To access the app open a browser and navigate to localhost:5000
