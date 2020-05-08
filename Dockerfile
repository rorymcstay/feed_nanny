FROM python:3.6-alpine

RUN mkdir -p /home

WORKDIR /home

ADD requirements.txt ./requirements.txt
RUN python -m pip install pip

RUN mkdir /data
RUN mkdir /data/content

# add selenium static js files
ADD ./requirements.txt /home/requirements.txt
ADD ./selector/selectorgadget_combined.min.js /data/content/selectorgadget_combined.js
ADD ./selector/selectorgadget_combined.css /data/content/selectorgadget_combined.css
ADD ./selector/initialise_gadget.js /data/content/initialise_gadget.js

RUN python -m pip install --upgrade pip
# Installing packages
RUN pip install -r ./requirements.txt

ENV SELECTOR_GADGET="/data/content"

# Copying over necessary files
COPY src /home/src
COPY settings.py ./settings.py
COPY nanny.py ./app.py

# Entrypoint
CMD ["python", "./app.py" ]
