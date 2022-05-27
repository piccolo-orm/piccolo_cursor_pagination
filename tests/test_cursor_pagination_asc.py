import typing as t
from unittest import TestCase

from fastapi import FastAPI, Request
from piccolo.columns import ForeignKey, Integer, Varchar
from piccolo.columns.readable import Readable
from piccolo.table import Table
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from piccolo_cursor_pagination.pagination import CursorPagination


class Director(Table):
    name = Varchar(length=100, required=True)


class Movie(Table):
    name = Varchar(length=100, required=True)
    rating = Integer()
    director = ForeignKey(references=Director)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s", columns=[cls.director.name])


app = FastAPI()


@app.get("/movies/")
async def movies(
    request: Request,
    __cursor: str,
    __previous: t.Optional[str] = None,
):
    try:
        previous = request.query_params["__previous"]
        if previous:
            paginator = CursorPagination(
                cursor=__cursor, page_size=2, order_by="id"
            )
            rows_result, headers_result = await paginator.get_cursor_rows(
                Movie, request
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
        paginator = CursorPagination(
            cursor=__cursor, page_size=2, order_by="id"
        )
        rows_result, headers_result = await paginator.get_cursor_rows(
            Movie, request
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


class TestCursorPaginationAsc(TestCase):
    def setUp(self):
        Director.create_table(if_not_exists=True).run_sync()
        Movie.create_table(if_not_exists=True).run_sync()

    def tearDown(self):
        Director.alter().drop_table().run_sync()
        Movie.alter().drop_table().run_sync()

    def test_cursor_pagination_asc(self):
        """
        If cursor is applied
        """
        Director.insert(
            Director(name="George Lucas"),
            Director(name="Ridley Scott"),
        ).run_sync()

        Movie.insert(
            Movie(name="Star Wars", rating=93, director=1),
            Movie(name="Blade Runner", rating=90, director=2),
            Movie(name="Alien", rating=91, director=2),
        ).run_sync()

        client = TestClient(app)
        response = client.get("/movies/", params={"__cursor": ""})
        self.assertTrue(response.status_code, 200)
        self.assertEqual(response.headers["next_cursor"], "Mw==")
        self.assertEqual(
            response.json(),
            {
                "rows": [
                    {
                        "id": 1,
                        "name": "Star Wars",
                        "rating": 93,
                        "director": 1,
                        "readable": "George Lucas",
                    },
                    {
                        "id": 2,
                        "name": "Blade Runner",
                        "rating": 90,
                        "director": 2,
                        "readable": "Ridley Scott",
                    },
                ]
            },
        )
        response = client.get("/movies/", params={"__cursor": "Mw=="})
        self.assertTrue(response.status_code, 200)
        self.assertEqual(response.headers["next_cursor"], "Mw==")
        self.assertEqual(
            response.json(),
            {
                "rows": [
                    {
                        "id": 3,
                        "name": "Alien",
                        "rating": 91,
                        "director": 2,
                        "readable": "Ridley Scott",
                    },
                ]
            },
        )

    def test_cursor_pagination_asc_previous(self):
        """
        If cursor ad previous is applied
        """
        Director.insert(
            Director(name="George Lucas"),
            Director(name="Ridley Scott"),
        ).run_sync()

        Movie.insert(
            Movie(name="Star Wars", rating=93, director=1),
            Movie(name="Blade Runner", rating=90, director=2),
            Movie(name="Alien", rating=91, director=2),
        ).run_sync()

        client = TestClient(app)
        response = client.get(
            "/movies/", params={"__cursor": "Mw==", "__previous": "yes"}
        )
        self.assertTrue(response.status_code, 200)
        self.assertEqual(response.headers["next_cursor"], "")
        self.assertEqual(
            response.json(),
            {
                "rows": [
                    {
                        "id": 1,
                        "name": "Star Wars",
                        "rating": 93,
                        "director": 1,
                        "readable": "George Lucas",
                    },
                    {
                        "id": 2,
                        "name": "Blade Runner",
                        "rating": 90,
                        "director": 2,
                        "readable": "Ridley Scott",
                    },
                ]
            },
        )

    def test_cursor_pagination_asc_previous_no_more_results(self):
        """
        If cursor is empty and previous is applied there is no
        more results, return empty rows
        """
        Director.insert(
            Director(name="George Lucas"),
            Director(name="Ridley Scott"),
        ).run_sync()

        Movie.insert(
            Movie(name="Star Wars", rating=93, director=1),
            Movie(name="Blade Runner", rating=90, director=2),
            Movie(name="Alien", rating=91, director=2),
        ).run_sync()

        client = TestClient(app)
        response = client.get(
            "/movies/", params={"__cursor": "", "__previous": "yes"}
        )
        self.assertTrue(response.status_code, 200)
        self.assertEqual(response.headers["next_cursor"], "")
        self.assertEqual(
            response.json(),
            {"rows": []},
        )
