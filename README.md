## notes

```
python3 venv venv
. venv/bin/activate
pip install -r requirements.txt
python run.py
```

### live reload

Install live reload...

https://chrome.google.com/webstore/detail/live-reload/jcejoncdonagmfohjcdgohnmecaipidc?hl=en

create a rule for http://localhost:5000/

pass the app as a string and set reload to true. see run.py...

uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
