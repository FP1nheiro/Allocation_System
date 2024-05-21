import os

class Config:
    SECRET_KEY = os.urandom(10)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'postgresql://postgres:admin@localhost/allocationSystem'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 300 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'exe'}  # Extensões permitidas
g