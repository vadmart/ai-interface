from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

template = Jinja2Templates(directory="templates")


@app.get("/")
def read_root(request: Request):
    return template.TemplateResponse("index.html", {"request": request})
