## Cursor pagination for Piccolo ORM

[Piccolo](https://github.com/piccolo-orm) is an great ecosystem that helps you create [ASGI](https://asgi.readthedocs.io/en/latest/) apps faster and easier. [LimitOffset](https://piccolo-api.readthedocs.io/en/latest/crud/piccolo_crud.html#pagination) is the default Piccolo pagination used by Piccolo Admin and Piccolo API. This package contains usage of cursor pagination which is suitable for large data sets and has better performance than ``LimitOffset`` pagination,
but it is **strictly optional** because it does not work with the Piccolo Admin and Piccolo API.

# Installation 

```bash
pip install piccolo_cursor_pagination
```
# Usage

Example usage of ``CursorPagination``:

```python
import typing as t

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from piccolo_api.crud.serializers import create_pydantic_model
from piccolo_cursor_pagination.pagination import CursorPagination

from home.tables import Task

app = FastAPI()

TaskModelOut: t.Any = create_pydantic_model(
    table=Task, include_default_columns=True, model_name="TaskModelOut"
)

@app.get("/tasks/", response_model=t.List[TaskModelOut])
async def tasks(
    request: Request,
    __cursor: t.Optional[str] = None,
    __previous: t.Optional[str] = None,
):
    try:
        previous = request.query_params["__previous"]
        paginator = CursorPagination(cursor=__cursor)
        rows_result, headers_result = await paginator.get_cursor_rows(
            Task, request
        )
        rows = await rows_result.run()
        headers = headers_result
        response = JSONResponse(
            {"rows": rows[::-1]},
            headers={
                "next_cursor": headers["cursor"],
            },
        )
    except KeyError:
        paginator = CursorPagination(cursor=__cursor)
        rows_result, headers_result = await paginator.get_cursor_rows(
            Task, request
        )
        rows = await rows_result.run()
        headers = headers_result
        response = JSONResponse(
            {"rows": rows},
            headers={
                "next_cursor": headers["cursor"],
            },
        )
    return response

@app.on_event("startup")
async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


@app.on_event("shutdown")
async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")
```
The ``CursorPagination`` stores the value of ``next_cursor`` in the response headers. 
We can then use the ``next_cursor`` value to get new set of results by passing 
``next_cursor`` to ``__cursor`` query parameter.

Full Piccolo ASGI app is in **example** folder or you can check [another example](https://github.com/sinisaos/piccolo-cursor-vue) with Vue frontend.

# Customization

The ``CursorPagination`` class has a default value of ``page_size`` and ``order_by``, 
but we can overide this value in constructor to adjust the way the results are displayed.

Example of displaying results in ascending order and page size is 10:

```python
paginator = CursorPagination(cursor=__cursor, page_size=10, order_by="id")
```

# Directions

The ``CursorPagination`` has the ability to move forward and backward. 
To go backward we have to pass ``__previous=yes`` in the query parameters.

Example usage of direction:

```
GET http://localhost:8000/tasks/?__cursor=NA== (forward)
GET http://localhost:8000/tasks/?__cursor=NA==&__previous=yes (backward)
```

# Limitations

You need to be aware that cursor pagination has several trade offs. The cursor must be based on a unique and sequential column in the table and the client can't go to a specific page because there is no concept of the total number of pages or results.

> **WARNING**: ``CursorPagination`` use Piccolo ORM ``id`` (PK type **integer**) column as unique and sequential column for pagination.