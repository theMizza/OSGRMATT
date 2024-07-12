from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.sql import select, update
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)


class QueryMaker:
    """
    Query maker class
    """
    def __init__(self, dburi: str, schema: str):
        self._dburi = dburi
        self._schema = schema
        self._engine = create_engine(self._dburi)
        self._metadata = MetaData()

    @property
    def schema(self):
        return self._schema

    @property
    def engine(self):
        return self._engine

    @property
    def metadata(self):
        return self._metadata

    def make_select_query(self,
                          table_name: str,
                          columns: list = None,
                          limit: int = None,
                          params: str = None):
        """
        Select query generator
        :param table_name: str
        :param schema: str
        :param columns: list
        :param limit: int
        :param params: str
        :return: query
        """
        for _ in range(3):
            try:
                table = Table(table_name, self.metadata, autoload_with=self.engine, schema=self.schema)
                if columns:
                    c_objs = [table.c[col] for col in columns]
                    query = select(*c_objs)
                else:
                    query = select(table)

                if params:
                    query = query.where(text(params))
                if limit:
                    query = query.limit(limit)
                break
            except Exception as query_exception:
                logger.warning("Make select query exception: %s", query_exception)
                continue
        else:
            raise ValueError("Make select query error!")
        return query

    def make_textbased_select_query(self,
                                    text_command: str,
                                    limit: int = None):
        """
        Text based query generator
        :param text_command: str
        :param limit: int
        :return: query
        """
        for _ in range(3):
            try:
                query = select(text(text_command))
                if limit:
                    query = query.limit(limit)
                break
            except Exception as query_exception:
                logger.warning("Make select query exception: %s", query_exception)
                continue
        else:
            raise ValueError("Make select query error!")

        return query

    def make_update_query(self, table_name: str, params: str, values: dict):
        """
        Update query generator
        :param table_name: str
        :param params: str
        :param values: dict
        :return: query
        """
        for _ in range(3):
            try:
                table = Table(table_name, self.metadata, autoload_with=self.engine, schema=self.schema)
                query = update(table).where(text(params)).values(values)
                break
            except Exception as query_exception:
                logger.warning("Make update query exception: %s", query_exception)
                continue
        else:
            raise ValueError("Make update query error!")
        return query

    def run_procedure(self, procedure_name: str, param: str):
        """
        Run procedure method - in work
        :param procedure_name: str
        :param param: str
        :return: list
        """
        connection = self.engine.raw_connection()
        logger.info("created connection: %s", connection)
        try:
            cursor = connection.cursor()
            logger.info("Created cursor: %s", cursor)
            cursor.execute(f"{procedure_name} @{param}")
            results = list(cursor.fetchall())
            cursor.close()
            connection.commit()
        except Exception as e:
            results = None
            logger.error("Run procedure error: %s", e)
        finally:
            connection.close()
        logger.info("Results list: %s", results)
        if results:
            for result in results:
                logger.info("Result: %s", result)


class Executor:
    """Request executor class"""
    def __init__(self, engine):
        self._engine = engine
        self._session = sessionmaker(self._engine)()

    @property
    def session(self):
        return self._session

    def execute(self, query, commit: bool = False):
        """
        execute request method, for update use commit = True
        """
        res = self.session.execute(query)
        if commit is True:
            self.session.commit()
        return res

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
