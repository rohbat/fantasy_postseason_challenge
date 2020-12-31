from flask_mongoengine import MongoEngine

db = MongoEngine()

def initialize_db(app):
    print(app.config['MONGODB_HOST'])
    db.init_app(app)