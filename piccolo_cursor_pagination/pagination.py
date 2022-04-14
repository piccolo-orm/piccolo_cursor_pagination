import base64
import typing as t
from dataclasses import dataclass

from fastapi.requests import Request
from piccolo.table import Table


@dataclass
class CursorPagination:
    """
    Used to cursor pagination.

    :param cursor:
        Value of cursor as a string.
    :param page_size:
        Value of page_size. Default to ``15``.
    :param order_by:
        Value of order_by descending order
        Default to ``-id``.
    """

    cursor: str
    page_size: int = 15
    order_by: str = "-id"

    async def get_cursor_rows(self, table: t.Type[Table], request: Request):
        # headers to adding next_cursor
        headers: t.Dict[str, str] = {}

        if self.order_by == "id":
            # query where limit is equal to page_size plus
            # one in ASC order
            query = table.select().order_by(
                table._meta.primary_key, ascending=True
            )
            query = query.limit(self.page_size + 1)

            # decoded query params cursor
            decoded_cursor = await self.decode_cursor(self.cursor, table)

            try:
                # preform operation if previous in query params
                previous = request.query_params["__previous"]
                if previous:
                    query = (
                        query.where(
                            table._meta.primary_key < int(decoded_cursor)
                        )
                        .order_by(table._meta.primary_key, ascending=False)
                        .limit(self.page_size)
                    )
                    rows = await query.run()
                    try:
                        # set new value to next_cursor
                        next_cursor = self.encode_cursor(str(rows[-1]["id"]))
                        headers["cursor"] = next_cursor
                        # return empty cursor if no more results
                        last_row = await table.select().limit(1).first().run()
                        if (
                            await self.decode_cursor(next_cursor, table)
                            == last_row["id"]
                        ):
                            headers["cursor"] = ""
                    except IndexError:
                        # no more results
                        headers["cursor"] = ""
            except KeyError:
                query = query.where(
                    table._meta.primary_key >= int(decoded_cursor)
                ).limit(self.page_size + 1)
                rows = await query.run()
                # set new value to next_cursor
                next_cursor = self.encode_cursor(str(rows[-1]["id"]))
                headers["cursor"] = next_cursor
                # if the last_row of whole data set is in rows, it means that
                # there are no more results, then we must use the first item
                # in the rows to get the correct result of the previous rows
                last_row = await (
                    table.select()
                    .limit(1)
                    .order_by(table._meta.primary_key, ascending=False)
                    .first()
                    .run()
                )
                if (
                    await self.decode_cursor(next_cursor, table)
                    == last_row["id"]
                ):
                    headers["cursor"] = self.encode_cursor(str(rows[0]["id"]))
        else:
            # query where limit is equal to page_size plus
            # one in DESC order
            query = table.select().order_by(
                table._meta.primary_key, ascending=False
            )
            query = query.limit(self.page_size + 1)

            # decoded query params cursor
            decoded_cursor = await self.decode_cursor(self.cursor, table)

            try:
                # preform operation if previous in query params
                previous = request.query_params["__previous"]
                if previous:
                    query = (
                        query.where(
                            table._meta.primary_key > int(decoded_cursor)
                        )
                        .order_by(table._meta.primary_key, ascending=True)
                        .limit(self.page_size)
                    )
                    rows = await query.run()
                    try:
                        # set new value to next_cursor
                        next_cursor = self.encode_cursor(str(rows[-1]["id"]))
                        headers["cursor"] = next_cursor
                        # return empty cursor if no more results
                        last_row = await (
                            table.select()
                            .limit(1)
                            .order_by(table._meta.primary_key, ascending=False)
                            .first()
                            .run()
                        )
                        if (
                            await self.decode_cursor(next_cursor, table)
                            == last_row["id"]
                        ):
                            headers["cursor"] = ""
                    except IndexError:
                        # no more results
                        headers["cursor"] = ""
            except KeyError:
                query = query.where(
                    table._meta.primary_key <= int(decoded_cursor)
                ).limit(self.page_size + 1)
                rows = await query.run()
                # set new value to next_cursor
                next_cursor = self.encode_cursor(str(rows[-1]["id"]))
                headers["cursor"] = next_cursor
                # if the last_row of whole data set is in rows, it means that
                # there are no more results, then we must use the first item
                # in the rows to get the correct result of the previous rows
                last_row = await (table.select().limit(1).first().run())
                if (
                    await self.decode_cursor(next_cursor, table)
                    == last_row["id"]
                ):
                    headers["cursor"] = self.encode_cursor(str(rows[0]["id"]))

        query = query.limit(self.page_size)
        return query, headers

    def encode_cursor(self, cursor: str) -> str:
        cursor_bytes = cursor.encode("ascii")
        base64_bytes = base64.b64encode(cursor_bytes)
        return base64_bytes.decode("ascii")

    async def decode_cursor(self, cursor: str, table: t.Type[Table]) -> int:
        if cursor is None:
            cursor = ""
        base64_bytes = cursor.encode("ascii")
        cursor_bytes = base64.b64decode(base64_bytes)
        initial_cursor = await (
            table.select()
            .order_by(table._meta.primary_key, ascending=False)
            .limit(1)
            .first()
            .run()
        )
        return (
            int(cursor_bytes.decode("ascii") or 0)
            if self.order_by == "id"
            else int(cursor_bytes.decode("ascii") or initial_cursor["id"])
        )
