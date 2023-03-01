FROM alpine

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    NASTOOL_CONFIG="/config/config.yaml" \
    PS1="\u@\h:\w \$ " \
    PUID=0 \
    PGID=0 \
    UMASK=000 \
    WORKDIR="/nas-tools"

COPY ./ ${WORKDIR}

WORKDIR ${WORKDIR}

RUN apk add --no-cache libffi-dev \
    && apk add --no-cache $(cat package_list.txt)
    
RUN ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo "${TZ}" > /etc/timezone

RUN ln -sf /usr/bin/python3 /usr/bin/python

RUN curl https://rclone.org/install.sh | bash

RUN curl https://dl.min.io/client/mc/release/linux-amd64/mc --create-dirs -o /usr/bin/mc \
    && chmod +x /usr/bin/mc

RUN pip install --upgrade pip setuptools wheel \
    && pip install cython \
    && pip install -r requirements.txt

RUN apk del libffi-dev \
    && npm install pm2 -g

RUN rm -rf /tmp/* /root/.cache /var/cache/apk/*

RUN python_ver=$(python3 -V | awk '{print $2}') \
    && echo "${WORKDIR}/" > /usr/lib/python${python_ver%.*}/site-packages/nas-tools.pth \
    && echo 'fs.inotify.max_user_watches=524288' >> /etc/sysctl.conf \
    && echo 'fs.inotify.max_user_instances=524288' >> /etc/sysctl.conf 

EXPOSE 3000
VOLUME ["/config"]
ENTRYPOINT ["/nas-tools/docker/entrypoint.sh"]