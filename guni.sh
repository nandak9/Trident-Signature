fuser -k 3131/tcp
gunicorn -w 4 -b 0.0.0.0:3131 start:app&

