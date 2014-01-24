from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date

Base = declarative_base()



### Class declarations go here
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    name = Column(String)
    password = Column(String)

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key = True, nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(64), nullable=False)

class Packing_list(Base):
    __tablename__ = "packing_lists"

    id = Column(Integer, primary_key = True, nullable=False)
    date = Column(Date, nullable=False)
    name = Column(String(64), nullable=False)

class item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key = True, nullable=False)
    sku = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    tag = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    sale_id = Column(Integer, nullable=False)
    packing_list_id = Column(Integer, nullable=False)

### End class declarations

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
