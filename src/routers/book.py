from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from src import celery
from src.database import create_session
from src.schemas.book import NewBook, TaskStatus
from src.services.book import BookService
from io import StringIO
import pandas as pd

from src.utils.service_result import handle_result

router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def read_items():
    return [{"name": "Foo"}]


@router.get("/{item_id}")
async def read_item(item_id: int, q: str = None, session: Session = Depends(create_session)):
    result = BookService(session).get_book(item_id)

    return handle_result(result)


@router.post("/add_book")
async def add_book(book: NewBook, session: Session = Depends(create_session)):
    result = BookService(session).add_book(book)

    return handle_result(result)


@router.get("/status/{task_id}")
async def add_book_status(task_id: str, session: Session = Depends(create_session)):
    result = await BookService(session).get_task_status(task_id)
    print(result)
    return handle_result(result)
    # return result
    # task = celery.app.AsyncResult(task_id)
    #
    # # print(task.state)
    # # print(task.result)
    # # print(task.info.get('current', ''))
    # if task.ready():
    #     return {
    #         "status": task.state,
    #         "result": task.result
    #     }
    # else:
    #     if task.state == 'PENDING':
    #         return {
    #             "status": task.state,
    #             "result": "Task is pending"
    #         }
    #     else:
    #         return {
    #             "status": task.state,
    #             "result": task.info.get('current', '')
    #         }


@router.post("/load_goodreads_books")
async def load_goodreads_books(file: UploadFile = File(...), session: Session = Depends(create_session)):
    if file.content_type == 'application/vnd.ms-excel' or file.content_type == 'text/csv':
        try:
            books = await BookService(session).process_goodreads_library_csv(file)
            print(handle_result(books))
        except ValueError as e:
            return JSONResponse(status_code=400, content={"message": str(e)})

        return handle_result(books)
    else:
        return JSONResponse(status_code=400, content={"message": "This endpoint accepts only CSV files."})
