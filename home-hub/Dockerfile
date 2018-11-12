# Use an official Python runtime as a parent image
FROM python:2.7.13

# Set the working directory to /app
WORKDIR /main

# Copy the current directory contents into the container at /app
COPY . /main

# Install any needed packages specified in requirements.txt
RUN pip install numpy
RUN pip install -r requirements.txt
RUN pip install -f https://download.mosek.com/stable/wheel/index.html Mosek==8.1.43

RUN mkdir ~/mosek/
ADD mosek.lic /main/
RUN cp /main/mosek.lic ~/mosek/

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME Powernet-Home-Hub-Application

# Run app.py when the container launches
CMD ["python", "init.py"]