# calm_the_dusty_butter
# CALM Database Update

Prerequisites:
- Docker (https://docs.docker.com/get-started/get-docker/)
  - Other container managers (ie. Podman) will likely work, but they have not been tested
- Clone repo to local computer
- CALM dataset (.sqlite)

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


Download field recorded ALT measurement dataset as CSV into ```/work/data``` directory

Copy current **Poduction** CALM database to ```/work/db``` directory
```
docker compose run --rm runner python /work/scripts/copy_db.py
```

Validate new data 
```
docker compose run --rm runner python /work/scripts/validate_csv.py
```

Stage new data for production
```
docker compose run --rm runner python /work/scripts/stage_alt.py
```

Insert new data into new Production DB
```
docker compose run --rm runner python /work/scripts/insert_measurements.py
```

Update geometries and views
```
docker compose run --rm runner python /work/scripts/update_geoms.py
```

