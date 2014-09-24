import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

engine = create_engine(config.DB_URI, echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    name = Column(String(64))
    password = Column(String(64))
    folder = Column(String(100))

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

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key = True, nullable=False)
    sku = Column(String(64), nullable=False)
    amount = Column(Integer, nullable=False)
    tag = Column(Integer, nullable=False)
    total = Column(Integer, nullable=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    packing_list_id = Column(Integer, ForeignKey('packing_lists.id'), nullable=False)

    sale = relationship("Sale", backref=backref("items", order_by=id))
    packing_list = relationship("Packing_list", backref=backref("items", order_by=id))
### End class declarations

def login(name, password):
    user = session.query(User).filter_by(name=name).one()
    if user.password == password:
        return user.id

def add_packing_list(name, date):
    packing_list =Packing_list(date=date, name=name)
    session.add(packing_list)
    session.commit()
    return packing_list.id

def add_sale(location, date):
    sale = Sale(date=date, location=location)
    session.add(sale)
    session.commit()
    return sale.id

def add_item(pl_id, sale_id, bar_code, value, amount):
    item = Item(sku=bar_code, amount=amount, tag=value, sale_id=sale_id, total=amount * value, packing_list_id=pl_id)
    session.add(item)
    session.commit()

def show_inventory():
    rows = session.query(Item.sku, func.sum(Item.amount), Item.tag).group_by(Item.sku).all()
    return rows

def set_folder(folder, session_user_id):
    user = session.query(User).filter_by(id=session_user_id).one()
    user.folder = folder
    session.commit()
    return True

def get_folder(session_user_id):
    user = session.query(User).filter_by(id=session_user_id).one()
    return user.folder

def get_packing_lists():
    return session.query(Packing_list).order_by(Packing_list.date).all()

def get_packing_list_by_id(list_id):
    return session.query(Item.sku, func.sum(Item.amount), Item.tag).group_by(Item.sku).filter(Item.packing_list_id==list_id).all()

def get_packing_list_name_by_id(list_id):
    return session.query(Packing_list.name).filter(Packing_list.id==list_id).one()

def get_sales_lists():
    return session.query(Sale).order_by(Sale.date).all()

def get_sale_by_id(list_id):
    return session.query(Item.sku, func.sum(Item.amount), Item.tag).group_by(Item.sku).filter(Item.sale_id==list_id).all()

def get_sale_name_by_id(list_id):
    return session.query(Sale.location).filter(Sale.id==list_id).one()

def search_by_sku(sku):
    print "^^^^^^^^", sku
    sales_rows = session.query(Item.sku, func.sum(Item.amount), Item.tag, Sale.location).group_by(Sale.location).filter(Item.sale_id==Sale.id).filter(Item.sku==sku).all()
    for row in sales_rows:
        print "row: ", row
    packing_list_rows = session.query(Item.sku, func.sum(Item.amount), Item.tag, Packing_list.name).group_by(Packing_list.name).filter(Item.packing_list_id==Packing_list.id).filter(Item.sku==sku).all()
    for row in packing_list_rows:
        print "row: ", row
    return packing_list_rows + sales_rows

def clear(file_type):
    connect_to_db()
    if file_type == "I":
        query = """DELETE from inventory"""
    else:
        query = """DELETE from comparison"""
    DB.execute(query, ())
    CONN.commit()
    print "All rows deleted"

def create_tables():
    Base.metadata.create_all(engine)
    session.commit()

def connect():
    engine = create_engine(config.DB_URI, echo=False) 
    session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))
    return session

if __name__ == "__main__":
    create_tables()
