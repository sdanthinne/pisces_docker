FROM tiangolo/uwsgi-nginx-flask:python3.8


COPY ./app /app

RUN apt update
RUN apt install -y ntp ca-certificates
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb 
RUN dpkg -i packages-microsoft-prod.deb
RUN apt update
RUN apt install -y apt-transport-https
RUN apt install -y dotnet-runtime-2.1

COPY ./Pisces ./Pisces
ARG CACHEBUST=1
RUN ls -tdr Pisces/binaries/* | head -1 > file_loc
RUN cp  $(cat file_loc)/* .
RUN ls
RUN ls *.gz | xargs -n1 tar -xzf 
