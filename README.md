# README #

# Vagrant #

### --- Create server Ubuntu 14.04 ###

Change into the directory, you want create vagrant and in `vagrant_setup/config.txt` set the proper configuration for project. Then:
```
#!

$ cd path/to/project
$ vagrant up
```

### --- Set up synced folders ###
Stop the VM by running:
```
#!

$ vagrant halt
```

Open the `Vagrantfile` and uncomment the synced folder line and set variables according to the `vagrant_setup/config.txt`:


```
#!ruby

config.vm.define "web" do |web|
     web.vm.box = "precise32"
     web.vm.hostname = "web"
     web.vm.network "private_network", ip: "192.168.101.11"
     web.vm.provision :shell, path: "vagrant_setup/scripts/provision.sh"
     # web.vm.synced_folder "APP_NAME", "APP_PATH/APP_NAME", owner: "APP_USER", group: "APP_USER_GROUP"
  end
```
Then run again:
```
#!

$ vagrant up
```


----------------------------------------------------------------------------------------------------------------------------------------------------------------
# Django #


### --- Create virtualenv with Python 3.4 ###

Change into the directory, you want create virtual environment:
```
#!

$ virtualenv --no-site-packages -p path/to/python3.4 {{venv-name}}
```

### --- The development server ###

Change into the outer mysite directory, if you haven’t already, and run the following commands:
```
#!

$ python manage.py runserver
```

### --- Creating a project / app ###

Project: 
```
#!

$ django-admin startproject <myproject>
```
To create your **app**, make sure you’re in the same directory as manage.py and type this command: 
```
#!

$ python manage.py startapp <appname>
```



### --- Superuser ###

Create superusers using the createsuperuser command:
```
#!

$ python manage.py createsuperuser --username=joe --email=joe@example.com
```



### --- Migrate ###

By running **makemigrations**, you’re telling Django that you’ve made some changes to your models (in this case, you’ve made new ones) and that you’d like the changes to be stored as a *migration*.


```
#!

$ python manage.py makemigrations <appname>
```

Now, run **migrate** again to create those model tables in your database:


```
#!

$ python manage.py migrate
```


### --- Running tests ###

In the terminal, we can run our test:
```
#!
$ python manage.py test <appname>
```






### --- Shell ###

To invoke the Python shell, use this command:
```
#!
$ python manage.py shell
```


### --- Install dependencies ###

Installing required dependencies on virtual environment:
```
#!
$ pip freeze > requirements.txt
$ pip install -r requirements.txt
```