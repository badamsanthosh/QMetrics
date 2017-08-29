sudo service nginx start
uwsgi --socket 127.0.0.1:8089 --module QADashBoardPro.wsgi