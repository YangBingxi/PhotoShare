from PhotoShare.app import app, db
from flask_script import Manager

manager = Manager(app)




if __name__ == '__main__':
    init_database()
    manager.run()
