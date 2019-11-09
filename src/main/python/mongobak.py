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
    log.debug(f"Retention: {config['backup'][b_dir]['retention']}")
    log.debug(f"Policy: {b_dir}")

    # -- run backup for each database
    if dbs_l and (type(dbs_l) is list):
        for dbs in dbs_l:
            log.info(f'Database name: {dbs}')
            log.info(f'creating backup file: {dbs}-{dt_label}.gz in {path}/{b_dir}/')

            cmd = ['mongodump']
            if conf['username'] and conf['password']:
                cmd += ['-u', conf['username'], '-p', conf['password']]
            cmd += [f'--authenticationDatabase={conf["authenticationDatabase"]}',
                    f'--archive={path}/{b_dir}/{dbs}-{dt_label}.gz', '--gzip', '--db', dbs]
            log.debug(f'command: {" ".join(cmd)}')
            out = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            log.info(out.stdout)
            r = True

            # -- apply retention policy
            _retainer(b_dir, dbs)

            config['last_run'] = dt_label
            config.save()

    return r


def _retainer(bp, db):
    ret_d = config['backup'][bp]['retention']
    if ret_d > 0:
        fm = FileManager(f"{config['backup']['path']}/{bp}")
        del_l = fm.ts_sorted_file('list', fn_pattern=f'.*{db}.*')
        if not ret_d > len(del_l):
            t = []
            # -- unpack filename
            for f in del_l:
                t += [f[0]]
            del_l = t[:len(t)-ret_d]
            log.debug(f'list of file to delete: {del_l}')
            fm.delete_files(f"{config['backup']['path']}/{bp}", del_l)
            del del_l, t
        log.info(f'applied retention policy: {bp}')


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
                log.info(f'checked last run: {last_run}')
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
