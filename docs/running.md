# Running Instructions

### Install ngrok
```
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
unzip ngrok-stable-linux-arm.zip
```
Note: above link is for arm based systems, get alternative download links from ngrok website

## Run ngrok
### Start a screen session for ngrok
```
screen -t ngrok -S ngrok
```

### Set ngrok http forwarding of port 8000
```
./ngrok http 8000
```

### Copy ngrok forwarding link
```
Looks something like: http://ad80951c.ngrok.io
```

### Detatch from screen session
```
ctrl + a, d
```

## Run brain
### Start a brain session for ngrok
```
screen -t brain -S brain
```

### Source env and run brain
```
source venv/bin/activate
./run.sh
```

### Detatch from screen session
```
ctrl + a, d
```

## View UI
```
Go to ngrok forwarding link
Something like: http://ad80951c.ngrok.io
```

## Re-attach to screens
### Re-attach to brain
```
screen -d brain
```

### Detatch from brain
```
ctrl + a, d
```

### Re-attach to ngrok
```
screen -d ngrok
```

### Detatch from ngrok
```
ctrl + a, d
```

## Next steps
[Contributing](contributing.md)