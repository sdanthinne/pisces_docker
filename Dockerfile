FROM tiangolo/uwsgi-nginx-flask:python3.8 


RUN apt update
RUN apt install -y ntp ca-certificates
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb 
RUN git clone https://github.com/Illumina/Pisces.git
RUN dpkg -i packages-microsoft-prod.deb
RUN apt update
RUN apt install -y apt-transport-https
RUN apt install -y dotnet-runtime-2.1 rename
RUN echo "$CACHEBUST"
RUN pip install eventlet shelljob flask_wtf Flask-BasicAuth
ARG CACHEBUST=1
COPY ./app /app
ARG VERSION=5.2.11.163
ENV NGINX_MAX_UPLOAD 50m
RUN tar -xzf Pisces/binaries/$VERSION/Pisces_$VERSION.tar.gz
RUN tar -xzf Pisces/binaries/$VERSION/CreateGenomeSizeFile_$VERSION.tar.gz

#COPY ./Pisces /Pisces
#RUN ls -tdr /Pisces/binaries/* | head -1 > file_loc
#RUN mkdir bin
#RUN cp  $(cat file_loc)/* bin/.
#RUN ls -d bin/*
#RUN ls -d bin/*.gz | xargs -I {} tar -xzf {} -C bin/
#RUN rm -r bin/*.gz
#RUN for file in bin/*; do mv "$file" "$(echo "$file" | sed 's/\_.*//')" ; done
#RUN rename -f 's/\_.*//' bin/*

