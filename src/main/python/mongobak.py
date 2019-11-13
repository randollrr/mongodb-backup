#!/usr/bin/env python3
import subprocess
import time

from auto_utils import config, log
from auto_fm import FileManager

__authors__ = ['randollrr']
__version__ = '1.0'

m_today = time.localtime()


def backup_mongo(dbs_l, path, conf):
    r = False

    # -- decide on backup rotation directory
    dt_label = time.strftime('%Y-%m-%d', m_today)
    b_dir = 'daily'
    week_days = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thrusday': 3,
                 'friday': 4, 'saturday': 5, 'sunday': 6}

    if m_today.tm_wday == week_days[config['backup']['weekly']['on']] and config['backup']['weekly']['retention'] > 0:
        b_dir = 'weekly'
    if m_today.tm_mday == config['backup']['monthly']['on'] and config['backup']['monthly']['retention'] > 0:
        b_dir = 'monthly'
    log.debug('Retention: {}'.format(config['backup'][b_dir]['retention']))
    log.debug('Policy: {}'.format(b_dir))

    # -- run backup for each database
    if dbs_l and (type(dbs_l) is list):
        for dbs in dbs_l:
            log.info('Database name: {}'.format(dbs))
            log.info('creating backup file: {}-{}.gz in {}/{}/'.format(dbs, dt_label, path, b_dir))

            cmd = ['mongodump']
            if conf['username'] and conf['password']:
                cmd += ['-u', conf['username'], '-p', conf['password']]
            cmd += ['--authenticationDatabase={}'.format(conf["authenticationDatabase"]),
                    '--archive={}/{}/{}-{}.gz'.format(path, b_dir, dbs, dt_label), '--gzip', '--db', dbs]
            log.debug('command: {}'.format(" ".join(cmd)))
            out = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            log.info(out.stdout)
            r = True

            # -- apply retention policy
            FileManager.retainer(b_dir, dbs)

            config['last_run'] = dt_label
            config.save()

    return r


def main():
    """
    * Create backup directory structure.
    * Run backup daily.
    * Rotate on a daily, weekly, monthly basis.
    """
    log.info('Starting mongodb backup script.')
    if config:
        # -- check directory and structure
        path = False
        if FileManager.dir_struct(config['backup']['path']):
            path = True
        # -- backup and rotate files
        if path:
            run = False

            last_run = config['last_run']
            if last_run:
                log.info('checked last run: {}'.format(last_run))
                if not last_run == time.strftime('%Y-%m-%d', m_today):
                    run = True
                else:
                    log.info('No need to run a backup at this time.')
            else:
                run = True

            if run:
                if backup_mongo(config['backup']['databases'], config['backup']['path'], config['db-instance']):
                    log.info('Backup process completed successfully.')
                else:
                    log.info('Backup process completed without errors.')
    else:
        log.error("Couln't retreive config file")


if __name__ == '__main__':
    main()
