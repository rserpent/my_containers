FROM python:3

WORKDIR /usr/src/app

RUN pip install aiopg aiohttp

COPY server.py ./

CMD [ "python", "./server.py" ] 