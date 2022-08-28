FROM python:3.9.13
WORKDIR /bookstore
COPY ./requirements.txt /bookstore/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /bookstore/requirements.txt
COPY . /bookstore