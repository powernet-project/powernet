FROM gcr.io/google-appengine/python

LABEL python_version=python

# Install redis
RUN wget http://download.redis.io/redis-stable.tar.gz && tar xvzf redis-stable.tar.gz && cd redis-stable && make

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

RUN mkdir /data && chown redis:redis /data
VOLUME /data
WORKDIR /data

# redis needs to talk on this port
EXPOSE 6379

# Run a WSGI server to serve the application. gunicorn must be declared as
# a dependency in requirements.txt.
CMD redis-server & celery -A app worker -l info & gunicorn -b :$PORT -t 60 app.wsgi