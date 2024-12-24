# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Install dependencies for pyodbc
RUN apt-get update \
    && apt-get install -y --no-install-recommends gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc-dev

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python modules
RUN pip install --no-cache-dir -r requirements.txt

# Command to run on container start
# CMD ["python3", "app.py"]
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]

