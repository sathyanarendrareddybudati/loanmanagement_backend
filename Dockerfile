FROM python:3.9-slim-buster

WORKDIR /loanmanagement_backend

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

# Copy the entire application code to the image
COPY . .

# Update the CMD instruction to run both Celery and Django
CMD celery -A loanmanagement_backend worker --loglevel=info & python3 manage.py runserver 0.0.0.0:8000

# Expose additional ports if necessary
EXPOSE 8000