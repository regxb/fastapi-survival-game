
# Гайд как запустить селери

НЕ ЗАБУДЬ 
```
poetry install
```

Вначале нужно запустить beat
```
celery --app=app_celery beat
```

Ну и сам селери  для виндавса
```
celery --app=app_celery worker --pool=solo --loglevel=info
```