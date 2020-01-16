# This is a simple docker image,
# which runs 'stress' command
# to simulate CPU and memory loads
FROM ubuntu:18.04

RUN apt update && apt install -y stress

ENTRYPOINT ["/usr/bin/stress"]