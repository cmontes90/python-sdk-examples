# Start from a base OS or another image
FROM ubuntu 

# Install Dependencies
RUN apt-get update  
RUN apt-get install python python-pip
                            
RUN pip install flask
RUN pip install flask-mysql

# Copy source code
COPY . /opt/source-code

# Specify Entrypoint
ENTRYPOINT FLASK_APP=/opt/source-code/app.py 


#######################################################

# This Docker File is for HTTPD Web Server

FROM centos:7

RUN yum -y update
RUN yum -y install httpd

COPY ./index.html /var/www/html/index.html

EXPOSE 80

CMD ["httpd", "-D", "FOREGROUND"]

