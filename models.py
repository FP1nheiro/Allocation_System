from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    allocation_method = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    blocks = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    tags = db.relationship('Tag', secondary='file_tags', back_populates='files')
    comments = db.relationship('Comment', backref='file', lazy=True)
    allocation_histories = db.relationship('AllocationHistory', backref='file', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<File {self.filename}>"

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    files = db.relationship('File', secondary='file_tags', back_populates='tags')

    def __repr__(self):
        return f"<Tag {self.name}>"

class FileTags(db.Model):
    __tablename__ = 'file_tags'
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)

    def __repr__(self):
        return f"<Comment {self.content[:20]}>"

class AllocationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    allocation_method = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
