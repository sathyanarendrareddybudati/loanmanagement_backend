FROM python:3.9-slim-buster

WORKDIR /loanmanagement_backend

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

# Copy the entire application code to the container
COPY . .

# Set the DJANGO_SETTINGS_MODULE environment variable
ENV DJANGO_SETTINGS_MODULE=loanmanagement_backend.settings

CMD celery -A loanmanagement_backend worker --loglevel=info && python manage.py runserver 0.0.0.0:8000

# Expose port 8000 for the Django application (if necessary)
EXPOSE 8000