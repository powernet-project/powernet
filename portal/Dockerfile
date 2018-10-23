FROM gcr.io/google-appengine/python

LABEL python_version=python

# Create a virtualenv for dependencies. This isolates these packages from
# system-level packages.
RUN virtualenv --no-download /env -p python

# Setting these environment variables are the same as running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Copy the application's requirements.txt and run pip to install all
# dependencies into the virtualenv.
ADD requirements.txt /app/
RUN pip install numpy
RUN pip install -r requirements.txt
RUN pip install -f https://download.mosek.com/stable/wheel/index.html Mosek==8.1.43

RUN mkdir ~/mosek/
ADD mosek.lic /app/
RUN cp /app/mosek.lic ~/mosek/

# Add the application source code.
ADD . /app/

# Run a WSGI server to serve the application. gunicorn must be declared as
# a dependency in requirements.txt.
CMD celery -A app worker -l info --purge --heartbeat-interval=60 --autoscale=10,3 & gunicorn -b :$PORT -t 100 app.wsgi