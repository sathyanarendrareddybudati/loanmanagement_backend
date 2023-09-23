
make install:
	pip install -r requirements.txt

make run:
	python manage.py runserver

make command:
	python manage.py insert_csvfiles <csvfile path>

make celery:
	celery -A loanmanagement_backend worker --loglevel=info