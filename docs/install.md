# Installation Instructions


## Device
### Get os onto device
```
Currently tested:
 - Beaglebone black | Stretch IoT | Debian 9.3
 - Should work on most *nix systems
```

### Clone repo
```
https://github.com/jakerye/openag-brain-quartz.git
```

### Go to repo directory
```
cd openag-brain-quartz
```

### Run install script
```
sudo ./install.sh
```

## Database
### Start postgres service
```
sudo systemctl start postgresql
```

### Login as postgres user
```
sudo -i -u postgres
```

### Enter postgres shell
```
psql
```

## Create `openag` user with password `openag`
```
CREATE USER openag WITH PASSWORD 'openag';
```

## Create `openag_brain` database owned by `openag` user
```
CREATE DATABASE openag_brain OWNER openag;
```

## Virtual Environment
### Create virtual environment
```
virtualenv -p python3 venv
```

### Source virtual environment
```
source venv/bin/activate
```

### Install python modules
```
pip install -r requirements.txt
```
