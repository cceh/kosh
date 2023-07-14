FROM python:3.8-alpine3.17
ADD . /tmp/kosh
RUN pip install /tmp/kosh && find /root /tmp -mindepth 1 -delete
USER 1000:1000
ENTRYPOINT ["kosh"]
