import model2

def create_user(session):
    user = model.User(name="Lynn", password="0441")
    model.session.add(user)

def main(session):
    create_user(session)
    model.session.commit()

if __name__ == "__main__":
    s = model2.connect()
    main(s)