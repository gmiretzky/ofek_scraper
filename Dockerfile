FROM techblog/selenium:latest
LABEL maintainer="tomer.klein@gmail.com"

ENV PYTHONIOENCODING utf-8
ENV LANG C.UTF-8

RUN apt update -yqq

RUN apt -yqq install python3-pip && \
    apt -yqq install libffi-dev && \
    apt -yqq install libssl-dev

RUN  pip3 install --upgrade pip --no-cache-dir && \
     pip3 install --upgrade setuptools --no-cache-dir &&\
     pip3 install schedule loguru

#Mount the config folder to the /app/config   -v /home/XXX/app/config:/app/config
RUN mkdir -p /app/config  

#Mount the output folder to the /app/output   -v /home/XXX/app/output:/app/output 
RUN mkdir -p /app/output

#Copy the main script 
COPY app /app

WORKDIR /app
 
CMD ["python","/app/run.py"]
