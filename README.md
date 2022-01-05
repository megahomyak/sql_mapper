# SQL MAPPER

Basically what it does is: it executes some SQL thru a database connector you
fed it, maps it to some model and gives to u. Also it can create tables

## How to install and import it

`pip install megahomyaks_sql_mapper` <- **WARNING: PACKAGE NAME IS DIFFERENT
                                          FROM THE PROJECT NAME**

`import sql_mapper` 

## Some abstract info about a model

    from sql_mapper import ModelBase

    class MyFirstModel(ModelBase):
        _tablename = "obvious"
        # You don't need to specify a _tablename if you will not create a table
        # for this model using an SQL executor OR insert it using parameter
        # marks from this mapper
        # (sql_executor.execute("INSERT INTO ?", [MyFirstModel("a", "b")]))

        first_field: str = "TEXT"
        # Value of each field is its datatype that will be used when SQL table
        # will be created (you don't need to fill these (you can preserve only
        # the typehint or place a stub as a value) if you will not create a
        # table from this model using an SQL executor)

        second_field = ""
        # Typehints are NOT necessary, they are used only for IDE type checking
        # (which is quite dumb in terms of Python, but it is easy to do and
        # can potentially help, so why not)

        _additional_table_lines = ""
        # Specify this if you need to append more lines to a table, such as
        # "PRIMARY KEY (some_field)"

## Some concrete info about a model + overall usage example

See [this file](tests/docs_example_test.py)

## About StringDump

There is a class called `StringDump` in
[string_dump.py](sql_mapper/string_dump.py), which
is a string that consumes other strings, and consists of formattable and
unformattable parts. One example can be found here, on line 27 (or not, I'm
not a megamind who can remember this reference and fix it when modifying the
linked file): [sql_mapper_test.py](tests/sql_mapper_test.py)

Don't forget about `raw`, kids

Now imma head out, gonna use some Tortoise ORM
