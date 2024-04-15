import time
from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.database import engine, Base
import logging.config
import config_ini
from src.routers import book
from fastapi.middleware.cors import CORSMiddleware
from .celery import app as celery
from .utils.app_exceptions import AppExceptionCase, app_exception_handler

app = FastAPI()


@app.exception_handler(AppExceptionCase)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)


Base.metadata.create_all(bind=engine)

log = logging.getLogger(config_ini.LOGGING_CONF)

origins = [
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.include_router(book.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@celery.task(bind=True)
def long_running_task(self):
    log.debug(self)
    # Example stages of the task
    log.debug("Starting long running task")
    time.sleep(3)
    self.update_state(state='PROGRESS', meta={'current': 'Getting data'})
    log.debug("Getting data")
    # Perform actual work here, e.g., getting data
    time.sleep(3)
    self.update_state(state='PROGRESS', meta={'current': 'Formatting data'})
    log.debug("Formatting data")
    # More work...
    time.sleep(3)
    self.update_state(state='PROGRESS', meta={'current': 'Adding rainbow'})
    log.debug("Adding rainbow")
    # Finalize
    return {'current': 'Returning expected data'}


@app.get('/task-status/{task_id}')
async def task_status(task_id: str):
    task = celery.AsyncResult(task_id)
    log.debug(task.state)
    if task.state == 'PENDING':
        return JSONResponse(content={'state': task.state, 'status': 'Pending...'})
    elif task.state == 'PROGRESS':
        return JSONResponse(content={
            'state': task.state,
            'status': task.info.get('current', '')
        })
    elif task.state == 'SUCCESS':
        return JSONResponse(content={'state': task.state, 'status': task.result})
    else:
        # Handle failure or unknown states
        return JSONResponse(content={'state': task.state, 'status': 'Error or unknown state'})


@app.post('/start-process/')
async def start_process():
    log.debug("Starting process")
    task = long_running_task.delay()  # Using delay to call the task asynchronously
    return JSONResponse(content={'task_id': task.id})


@app.post('/')
async def test():
    return {"message": "Hello World 232"}


@app.get("")
def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}"}


# @app.post("/items/")
# def create_item(name: str, db: AsyncSession = Depends(get_db)):
#     # new_item = ExampleModel(name=name)
#     # db.add(new_item)
#     # await db.commit()
#     # return {"id": new_item.id, "name": new_item.name}
#     pass


# @app.get("/test")
# def test():
#     model = BertModel()
#     tokens = model.get_tokens(
#         "Grandpa Pig buys George a dinosaur balloon but George keeps letting it go. Who will rescue the balloon when it starts to float away?\n A new adventure featuring Peppa and George.")
#
#     log.debug(tokens)
#
#     print(model.get_tokens(
#         "Grandpa Pig buys George a dinosaur balloon but George keeps letting it go. Who will rescue the balloon when it starts to float away?\n A new adventure featuring Peppa and George.")
#     )
#
#     return model.get_tokens(
#         "Grandpa Pig buys George a dinosaur balloon but George keeps letting it go. Who will rescue the balloon when it starts to float away?\n A new adventure featuring Peppa and George.")
#
#
# @app.get("/books")
# def get_books(db: Session = Depends(get_db)):
#     return BookService.get_books(db, 10)
#
#
# @app.get("/books/{book_id}")
# def get_book(book_id: int, db: Session = Depends(get_db)):
#     pass
#     # return BookService.get_book(db, book_id)
#
#
# @app.post("/recommend_books")
# def recommend_books():
#     pass
#
#
# @app.post("/load_goodreads_books")
# def load_goodreads_books():
#     pass
