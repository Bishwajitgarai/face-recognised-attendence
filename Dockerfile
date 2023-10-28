From python:3.8
Label maintainer = 'bishwajitgarai2520@gmail.com'

WORKDIR /usr/src/app

ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install pipenv
# RUN pipenv shell
COPY Pipfile ./
COPY Pipfile.lock ./
RUN pipenv install
RUN pipenv install gunicorn
COPY . .

RUN chmod a+x entrypoint.sh

EXPOSE 3000
ENTRYPOINT ./entrypoint.sh