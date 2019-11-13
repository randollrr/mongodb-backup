# MongoDB Automated Backups
Supports mongoDB 3.2+.

## Install and configure backup script
1. Clone the project:
   
   `sudo git clone https://github.com/randollrr/mongodb-backup.git /opt/mongodb-backup`
2. Setup backup schedules using cron:
   
   `cd /opt/mongodb-backup`
   `sudo cp mongobak.sh /etc/cron.daily/`
3. Update the config file:
   - add database name
   - update retention policy

   `sudo vi /opt/mongodb-backup/src/main/python/config.json`
 
