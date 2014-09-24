import model2

def load_master(s):
    f = open("seed_data.py")
    rows = f.read().split("\n")
    
    for line in rows:
        print line
        row = line.split("|")
        name = row[0]
        password = row[1]
        folder = row[2]

        user = model2.User(name=name, password=password, folder=folder)

        model2.session.add(user)
        print "Added ", user.name
    
    f.close()

def main(s):
    # model2.clear("I")
    load_master(s)
    model2.session.commit()

if __name__ == "__main__":
    s = model2.connect()
    main(s)