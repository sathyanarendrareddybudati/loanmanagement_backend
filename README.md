## Getting started
To get started with Logging, follow these steps:

- Clone the repository to your local machine
- Install the required packages listed in requirements.txt
- Set up your MYSQL database and create a table for storing logs
- Start the Djnago application using `make run` or  `python manage.py runserver`
- To start the celery using `celery -A loanmanagement_backend worker --loglevel=info`
- To run the command use this `python manage.py insert_csvfiles <csvfile path>`


## Note
- All requests must have Authorization token in headers
- To install all packages using `make install` or `pip install -r requirements.txt`
- Token must pass like in headers `Authorization : Token <Token value>`