# Use an official Python runtime as a parent image
FROM python:2.7.13

# Set the working directory to /app
WORKDIR /main

# Copy the current directory contents into the container at /app
COPY . /main

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME Powernet-Home-Hub-Application

# Run app.py when the container launches
CMD ["python", "init.py"]