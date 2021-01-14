##**Create uwsgi+flask111 docker image**

## 1. purpose:
	to build a kms(fastAPI+uvloop+kms) docker image based on
	python:3.8-slim image

## 2. Dockerfile

1.  docker file

	```
	FROM python:3.8-slim

	COPY ./sources.list  /etc/apt/sources.list
	COPY ./requirements.txt  /kms/requirements.txt

	RUN apt-get install -y --no-install-recommends \
			# libpq-dev \
		&& set -ex \
		&& pip install --no-cache-dir \
			-r  /kms/requirements.txt \
			-i "https://pypi.tuna.tsinghua.edu.cn/simple" \
		&& rm -rf /tmp/* \
		&& apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
		&& rm -rf /var/lib/apt/lists/*
	WORKDIR /kms
	ADD ./kms /kms
	EXPOSE  3000
	CMD uvicorn main:app --reload --port 3000  --host 0.0.0.0
	```

2. requirements.txt content:

	```
	aiofiles==0.5.0
	attrs==20.2.0
	certifi==2020.6.20
	chardet==3.0.4
	click==7.1.2
	fastapi==0.61.1
	h11==0.9.0
	httptools==0.1.1
	idna==2.10
	iniconfig==1.0.1
	MarkupSafe==1.1.1
	packaging==20.4
	pluggy==0.13.1
	py==1.9.0
	pydantic==1.6.1
	PyJWT==1.7.1
	pymongo==3.11.0
	pyparsing==2.4.7
	#pytest==6.1.1
	requests==2.24.0
	six==1.15.0
	starlette==0.13.6
	toml==0.10.1
	urllib3==1.25.10
	uvicorn==0.11.8
	uvloop==0.14.0
	websockets==8.1
	```

## 3. command to build image:

	docker image build -t whsasf/kms:v1  .
