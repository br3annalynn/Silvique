import model2

def load_master(s):
    f = open("seed_data.py")

    for line in f:
        print line
    

def main(s):
    load_master(s)

if __name__ == "__main__":
    s = model2.connect()
    main(s)