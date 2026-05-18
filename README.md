# CALM Database Updater

Prerequisites:
- Docker (https://docs.docker.com/get-started/get-docker/)
  - Other container managers (e.g. Podman) will likely work, but they have not been tested
- Clone repo to local computer
- CALM dataset (.sqlite)



After cloning repo, build the container:
```
docker compose build
```
---

## Now you are ready to update the CALM database

---
Order of Operations

1. Update update_config.yaml with this year's information
   - source database path
   - output database path
   - input CSV path
   - Recorded by
   - Updated by
2. Copy Production database - This creates new Production DB
3. Validate measurements CSV
4. Stage ALT measurements
5. Insert ALT measurements to new Production DB
6. Update geometries and final validations
---

### Steps:
- Download current production database (.sqlite) into the ```/work/db``` directory of the local repo
- Download field recorded ALT measurement dataset as CSV into the ```/work/data``` directory of the local repo


### This program will:
- Validate new ALT data in CSV
- Stage new data for production
- Insert new data into new Production DB


Run
```
docker compose run --rm runner python /work/scripts/main.py 
```


---

Troubleshooting
- Is Docker running?
- Check paths in update_config.yaml