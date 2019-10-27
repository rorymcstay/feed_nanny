FROM python:3.6-alpine

RUN mkdir -p /home

WORKDIR /home

ADD requirements.txt ./requirements.txt
RUN python -m pip install pip

# Installing packages
RUN pip install -r ./requirements.txt

# Copying over necessary files
COPY src ./src
COPY settings.py ./settings.py
COPY nanny.py ./app.py

# Entrypoint
CMD ["python", "./app.py" ]
