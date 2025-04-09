# Use official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install wheel
RUN pip install wheel

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install gunicorn

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start Django application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "pyc_warmup.wsgi:application"]
