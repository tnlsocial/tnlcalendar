FROM python:3.11.2-slim
EXPOSE 8000
COPY . /home
WORKDIR /home
RUN pip3 install -r requirements.txt
CMD ["gunicorn", "wsgi:application", "-w", "2", "--threads", "2", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
