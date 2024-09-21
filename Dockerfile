FROM techblog/selenium:latest
LABEL maintainer="gmiretzky@gmail.com"

ENV PYTHONIOENCODING utf-8
ENV LANG C.UTF-8

RUN apt update -yqq

RUN apt -yqq install python3-pip && \
    apt -yqq install libffi-dev && \
    apt -yqq install libssl-dev

RUN  pip3 install --upgrade pip --no-cache-dir && \
     pip3 install --upgrade setuptools --no-cache-dir 
     
RUN mkdir -p /app/config
RUN mkdir -p /app/output

COPY app /app

WORKDIR /app
 
CMD ["python","/app/run.py"]
