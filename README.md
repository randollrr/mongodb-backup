# Installation

## Install Python 3.7 on CentOS 7
1. yum install gcc openssl-devel bzip2-devel libffi-devel
2. cd /usr/src
3. wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz
4. tar xzf Python-3.7.3.tgz
5. rm Python-3.7.3.tgz
6. cd Python-3.7.3
7. ./configure --enable-optimizations
8. make altinstall
9. [validate:] python3.7 -V

### Post install
* cp /usr/local/bin/python3.7 /usr/bin/
* cd /usr/bin/
* ln -s python3.7 python3

## Install backup script
git clone https://github.com/randollrr/mongodb-backup.git

## Copy cron job into /etc/cron.daily/
cp mongobak-cron /etc/cron.daily/mongobak-cron

