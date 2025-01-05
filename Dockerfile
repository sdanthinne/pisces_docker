FROM tiangolo/uwsgi-nginx-flask:python3.8 


RUN apt-get update
RUN apt-get install -y ntp ca-certificates mailutils
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb 
RUN git clone https://github.com/Illumina/Pisces.git
RUN dpkg -i packages-microsoft-prod.deb
RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN apt-get install -y dotnet-runtime-2.1 rename
RUN pip install eventlet shelljob flask_wtf Flask-BasicAuth pyyaml
COPY ./app /app
COPY config.yaml /app/config.yaml
ARG VERSION=5.2.11.163
ENV NGINX_MAX_UPLOAD 150m
RUN tar -xzf Pisces/binaries/$VERSION/Pisces_$VERSION.tar.gz
RUN tar -xzf Pisces/binaries/$VERSION/CreateGenomeSizeFile_$VERSION.tar.gz

