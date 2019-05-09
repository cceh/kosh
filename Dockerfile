# cceh/kosh
FROM alpine:latest
ADD . /tmp/kosh
RUN \
#
# packages
apk --no-cache add \
  py3-lxml \
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
