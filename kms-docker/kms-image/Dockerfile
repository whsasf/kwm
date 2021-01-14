FROM python:3.8-slim

COPY ./sources.list  /etc/apt/sources.list
COPY ./requirements.txt  /kms/requirements.txt
# RUN apt-get update \
# 	&& apt-get install -y --no-install-recommends \
# 		gcc \
# 		#libc-dev \
# 		#uuid-dev \
# 	    #libssl-dev \
# 		#libpcre3-dev \
# 	&& pip install --no-cache-dir -r /requirements.txt -i "https://pypi.tuna.tsinghua.edu.cn/simple" \
#         && rm -rf /tmp/* \
# 	&& apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
# 	&& rm -rf /var/lib/apt/lists/* \

RUN apt-get install -y --no-install-recommends \
		# libpq-dev \
	&& set -ex \
	&& pip install --no-cache-dir \
		-r  /kms/requirements.txt \
		#-i "https://pypi.tuna.tsinghua.edu.cn/simple" \
	&& rm -rf /tmp/* \
	&& apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
	&& rm -rf /var/lib/apt/lists/*
WORKDIR /kms
ADD ./kms /kms
EXPOSE  3000
CMD uvicorn main:app --reload --port 3000  --host 0.0.0.0