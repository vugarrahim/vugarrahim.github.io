# Fabfile to:
# - update the remote system(s)
#    - download and install an application

# Some tutorials:
#   - https://www.digitalocean.com/community/tutorials/how-to-use-fabric-to-automate-administration-tasks-and-deployments
#   - http://docs.fabfile.org/en/latest/tutorial.html
#   - https://confluence.atlassian.com/pages/viewpage.action?pageId=270827678
from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
# Import Fabric's API module
from fabric.api import *

import os
location = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), "..", x))


# Set the remote
# $: echo "export VAR=value" >> ~/.profile
if os.environ.get('ROOTPASS'):
    env.hosts = [os.environ.get('ROOTIP'), ]
    env.user = os.environ.get('ROOTUSER')
    env.password = os.environ.get('ROOTPASS')
    app_user_pasw = os.environ.get('APPUSERPASS')



# Deployment parametres
app_name = '#{APP_NAME}'
app_user = '#{APP_USER}'
app_path = '#{APP_PATH}'
main_app = local_supervisor = app_supervisor = app_name
app_dir = location(app_name)
dev_dir = app_dir
git_dir_serv = app_path




# ------------------------------------------------------------
# Settings.py

def switch_debug(frm, to):
    """
    >>> text = 'salam %(name)s, yaxisan? Men %(me)s'
    >>> text % ({'name':'ahmed', 'me': 'sadiq'})
    """
    local('cp %(app_dir)s/%(main_app)s/settings.py %(app_dir)s/%(main_app)s/settings.bak' % (
        {'app_dir': app_dir, 'main_app': main_app}))

    sed = "sed 's/^DEBUG = %(from)s/DEBUG = %(to)s/' %(app_dir)s/%(main_app)s/settings.bak > %(app_dir)s/%(main_app)s/settings.py"
    local(sed % ({
                     'from': frm,
                     'to': to,
                     'app_dir': app_dir,
                     'main_app': main_app
                 }))

    local('rm %(app_dir)s/%(main_app)s/settings.bak' % ({'app_dir': app_dir, 'main_app': main_app}))


def prepare():
    switch_debug('True', 'False')
    backup_local()
    switch_debug('False', 'True')


def backup_local():
    local('git pull')
    local('git add .')

    print('Enter commit comment:')
    comment = raw_input()

    local('git commit -m "%s"' % comment)
    local('git push')


# ------------------------------------------------------------
# Decerators



@_contextmanager
def virtualenv():
    """
        Activates the virtual environment
        - http://stackoverflow.com/a/5359988/968751
    """
    venv_activate = 'source %(app)s/bin/activate' % ({'app': git_dir_serv})
    with cd(app_dir):
        with prefix(venv_activate):
            yield


@_contextmanager
def virtualenv_lc():
    """
        Activates the virtual environment locally
    """
    venv_activate = 'source %(app)s/bin/activate' % ({'app': git_dir_serv})
    with lcd(dev_dir):
        with prefix(venv_activate):
            yield


# ------------------------------------------------------------
# Git functions
def git_fetch():
    """
        Logins to the server as the app user of Ubuntu
        and gets latest updates from git and replaces files accordingly
    """
    with settings(user=app_user, password=app_user_pasw):
        with cd(git_dir_serv):
            run('pwd')
            # run('ls -l')
            # run('git status')
            run('git fetch origin master')
            run('git reset --hard origin/master')
            run('git status')
            switch_server_debug('True', 'False')
            run('git status')


def git_revert(commit):
    """
        Revert back to certain commit.
        http://stackoverflow.com/a/4114122/968751

        - Usage:
          $: fab git_revert:commit='f4f6dab'
    """
    with settings(user=app_user, password=app_user_pasw):
        with cd(app_dir):
            run('git checkout -b old-state %s' % commit)
            switch_server_debug('True', 'False')
            run('git status')


# ------------------------------------------------------------
# Server commands for deploy


def install2server():
    """
        Install libraries to server from local
    """
    with cd(app_dir):
        print('Enter library you want install to server:')
        library = raw_input()

        sudo('apt-get install -y %s' % library)


def switch_server_debug(frm, to):
    """
    >>> text = 'salam %(name)s, yaxisan? Men %(me)s'
    >>> text % ({'name':'ahmed', 'me': 'sadiq'})
    """
    run('cp %(app_dir)s/%(main_app)s/settings.py %(app_dir)s/%(main_app)s/settings.bak' % (
        {'app_dir': app_dir, 'main_app': main_app}))

    sed = "sed 's/^DEBUG = %(from)s/DEBUG = %(to)s/' %(app_dir)s/%(main_app)s/settings.bak > %(app_dir)s/%(main_app)s/settings.py"
    run(sed % ({
                   'from': frm,
                   'to': to,
                   'app_dir': app_dir,
                   'main_app': main_app
               }))

    run('rm %(app_dir)s/%(main_app)s/settings.bak' % ({'app_dir': app_dir, 'main_app': main_app}))


def update_codes():
    """
        Restart Supervisor and Ngnix for runing changed codes
    """
    with cd(app_dir):
        sudo('supervisorctl restart %s' % app_supervisor)
        # sudo('supervisorctl restart %s-celery' % app_supervisor)
        sudo('sudo service nginx restart')


def check_requirements():
    """
        Installs requirements for the app
    """
    with settings(user=app_user, password=app_user_pasw):
        with cd(app_dir):
            with virtualenv():
                run('pip freeze')
                run('pip install -r requirements.txt')


def server_syncdb():
    """
        Installs DB changes of App
    """
    with settings(user=app_user, password=app_user_pasw):
        with cd(app_dir):
            with virtualenv():
                # run('python manage.py makemigrations')
                run('python manage.py migrate')


def run_celery(state='restart'):
    """
        Activate celery
    """
    with settings(user=app_user, password=app_user_pasw):
        with cd(app_dir):
            with virtualenv():
                run('celery multi %(do)s -A %(main_app)s w1 --beat -l error' % ({'do': state, 'main_app': main_app}))
                run('cat w1.log')

def check_logs(path='../logs/django_requests.log'):
    """
        Check logs
    """
    with settings(user=app_user, password=app_user_pasw):
        with cd(app_dir):
            with virtualenv():
                # run('cat %(log_path)s ' % ({'log_path': path,}))
                # run('pwd && ls -l')
                # run('echo "" > %(log_path)s ' % ({'log_path': path,}))
                run('cat %(log_path)s ' % ({'log_path': path,}))
                # run('cat w1.log')


# ------------------------------------------------------------

def deploy():
    """
        Deploy to the server
    """
    # get latest codes
    git_fetch()

    # check libraries
    check_requirements()

    # check DB
    server_syncdb()

    # run latest code
    update_codes()


def debug_server():
    with settings(user=app_user, password=app_user_pasw):
        with cd(git_dir_serv):
            switch_server_debug('False', 'True')

    # run latest code
    update_codes()

# ------------------------------------------------------------

def run_celery_lc(state='restart'):
    """
        Activate celery
    """
    with settings(user=app_user):
        with lcd(dev_dir):
            with virtualenv_lc():
                # local('celery multi %(do)s -A %(main_app)s w1 --beat -l info' % ({'do': state, 'main_app': main_app}))
                local('pip freeze')

def vagrant():
    with lcd(dev_dir):
        local('sudo supervisorctl restart %s' % local_supervisor)
        # local('sudo supervisorctl restart %s-celery' % local_supervisor)
        local('sudo service nginx restart')


def sync_local():
    with lcd(dev_dir):
        with prefix('. %s/../bin/activate' % dev_dir):
            local('pip install -r requirements.txt')
            local('python manage.py migrate')
            local('python manage.py collectstatic')
            local('pwd')
            local('ls -l')