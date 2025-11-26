from twisterlab.database.session import engine, Base
from sqlalchemy import inspect
from twisterlab.database.models import agent as agent_model

inspector = inspect(engine)
print('tables:', inspector.get_table_names())
