# https://docs.docker.com/engine/reference/builder/
FROM ubuntu:22.04 as cpp-server
COPY cpp-server/docker-start.bash /proj/docker-start.bash
WORKDIR /proj
EXPOSE 12555
RUN apt -y update && apt -y upgrade
RUN apt -y install g++ make net-tools
CMD ["./docker-start.bash"]

FROM ubuntu:22.04 as login-server
COPY python-login-server/docker-start.bash /proj/docker-start.bash
WORKDIR /proj
EXPOSE 10000
RUN apt -y update && apt -y upgrade
RUN apt -y install python3.10 pip
RUN pip3 install mysql-connector-python 
CMD ["./docker-start.bash"]
