# Deploy

create systemd service in `/etc/systemd/system`

```
[Unit]
Description=MPC_RUNNER
After=multi-user.target

[Service]
Type=simple
User=root
Restart=always
WorkingDirectory=/home/key_alex/mpc_experiment
ExecStart=/home/key_alex/mpc_experiment/.venv/bin/python3 mvp_mpc.main_mpc.py


[Install]
WantedBy=multi-user.target
```

To start the service execute the following commands

```
sudo systemctl daemon-reload
sudo systemctl enable start experiment_mpc.service
sudo systemctl status experiment_mpc.service
sudo systemctl start experiment_mpc.service
```

To look at the logs of the service
```
journalctl -u experiment_mpc.service
```
