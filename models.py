from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Composition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text, nullable=False)
    features = db.Column(db.PickleType)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    # pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.relationship('Author', backref=db.backref('compositions', lazy=True))

    def __repr__(self):
        return '<Composition %r>' % self.title


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    img_url = db.Column(db.String(1000), nullable=True)
    # class_label = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Author %r>' % self.name


