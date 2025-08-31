# ClassyFire 🔥

_Classify research articles_


## Requirements

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package and project manager
- Make


## Deploying the website locally

Follow these instructions to run Classy Fire locally. First, run:

```bash
make install
```

Then, edit the `.env` file in the root directory of the repository with the following content:

```env
CLASSYFIRE_LANG=en  # "en" or "fr"
```


Finally, run:

```bash
make run
```

The website will be available at [http://localhost:8501](http://localhost:8501).


## Importing CSV data

To import CSV data, run the following command:

```bash
uv run classyfire/scripts/import_csv.py <path-to-csv-file>
```


## Deployment

<details>
<summary>Tips for manual deployment</summary>

### Service

Create the file `classyfire.service`:
```ini
[Unit]
Description=ClassyFire server
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/classyfire/root
ExecStart=/usr/bin/make run
Restart=always
RestartSec=5
Environment=PATH=/usr/local/bin:/usr/bin:/bin:/path/to/uv/dir

[Install]
WantedBy=multi-user.target
```
Make sure the `Environment` contains the path to the directory that contains the `uv` executable (shown by `which uv`)

Copy or link the file to `/etc/systemd/system/classyfire.service`:
```bash
sudo ln -s /path/to/classyfire/root/classyfire.service /etc/systemd/system/classyfire.service
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable classyfire.service
sudo systemctl start classyfire.service
sudo systemctl status classyfire.service
journalctl -u classyfire.service -f
```


### Database backup

Run
```bash
crontab -e
```

Append the lines:
```bash
# Classyfire backups
# Daily (midnight)
0 0 * * * cp /absolute/path/to/db.json /absolute/path/to/backups/01_db_daily.json
# Weekly (Sunday midnight)
0 0 * * 0 cp /absolute/path/to/db.json /absolute/path/to/backups/02_db_weekly.json
# Monthly (1st day of month midnight)
0 0 1 * * cp /absolute/path/to/db.json /absolute/path/to/backups/03_db_monthly.json
# Every 3 months (January, April, July, October 1st at midnight)
0 0 1 1,4,7,10 * cp /absolute/path/to/db.json /absolute/path/to/backups/04_db_quarterly.json
```

Check with
```bash
crontab -l
```
</details>
