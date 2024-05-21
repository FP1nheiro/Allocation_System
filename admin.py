from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, File, Tag, Comment, AllocationHistory

def create_admin(app):
    admin = Admin(app, name='File Upload System Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(File, db.session))
    admin.add_view(ModelView(Tag, db.session))
    admin.add_view(ModelView(Comment, db.session))
    admin.add_view(ModelView(AllocationHistory, db.session))
