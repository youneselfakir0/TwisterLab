from sqlalchemy import inspect

from twisterlab.database.session import engine

inspector = inspect(engine)
print("tables:", inspector.get_table_names())
