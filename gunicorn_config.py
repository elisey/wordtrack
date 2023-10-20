# info: https://docs.gunicorn.org/en/stable/settings.html

bind = "0.0.0.0:8000"
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 2
max_requests = 1000
