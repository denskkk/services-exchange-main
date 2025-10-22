runserver:
	python src/manage.py runserver
format:
	black .
	ruff check . -n --select I --fix
lint:
	mypy .
css:
	npx tailwindcss -i ./src/static/src/input.css -o ./src/static/styles.css
prepare:
	make format
	make css
dumpdata:
	docker exec -it web python manage.py dumpdata --indent=2 --output=./exchange/fixtures/categories.json exchange.Category
dev_up:
	docker compose -f docker-compose.dev.yml up
dev_down:
	docker compose -f docker-compose.dev.yml down
test:
	docker exec -it web python manage.py test