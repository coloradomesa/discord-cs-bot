FROM python:3.6
COPY . /app
WORKDIR /app
RUN wget "http://ftp.us.debian.org/debian/pool/main/o/opus/libopus0_1.2.1-1_amd64.deb" && dpkg -i "libopus0_1.2.1-1_amd64.deb"
RUN pip install -r requirements.txt
CMD python3 -m csbot