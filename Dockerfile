# cceh/kosh
FROM alpine:altest
ADD . /tmp/kosh
RUN \
#
# packages
apk --no-cache add \
  py3-lxml \
  py3-setuptools \
  py3-urllib3 \
  python3 && \
apk --no-cache --virtual build add \
  make \
  py3-pip && \
#
# kosh
make -C /tmp/kosh && \
#
# cleanup
apk del --purge build && \
find /root /tmp -mindepth 1 -delete
#
# runtime
ENTRYPOINT ["/usr/bin/kosh"]
