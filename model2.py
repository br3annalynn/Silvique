from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

engine = create_engine("sqlite:///inventory.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

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

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key = True, nullable=False)
    sku = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    tag = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
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
    item = Item(sku=bar_code, amount=amount, tag=value, total=value * amount, sale_id=sale_id, packing_list_id=pl_id)
    session.add(item)
    session.commit()

def show_inventory():
    rows = session.query(Item.sku, func.sum(Item.amount), Item.tag, Item.total).group_by(Item.sku).all()
    print "###########rows: ", rows
    return rows


def main():
    pass

if __name__ == "__main__":
    main()
