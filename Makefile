
help:
	@echo "Available commands:"
	@echo "  make build   - build docker images"
	@echo "  make up      - start Jupyter workbench"
	@echo "  make db      - rebuild SpatiaLite database (calm_v01.sqlite)"

build:
	docker compose build

up:
	docker compose up workbench

down:
	docker compose down

py:
	docker compose run --rm runner python

db:
	docker compose run --rm runner  bash -lc " \
		rm -f /work/db/calm_v01.sqlite && \
		spatialite /work/db/calm_v01.sqlite 'SELECT InitSpatialMetadata(1);' && \
		spatialite /work/db/calm_v01.sqlite < /work/sql/sqlite_calm_v0001e.sql \
	"