import os
import uuid
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
from config import Config
from models import db, File, AllocationHistory, Tag, Comment
from allocation import allocate_file
from admin import create_admin

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

create_admin(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    files = File.query.all()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('file')
    for file in files:
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())
            file_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{filename}")
            file.save(file_path)

            file_size_bytes = os.path.getsize(file_path)
            block_size = 4096  # 4KB
            size = (file_size_bytes + block_size - 1) // block_size  # Calculate number of blocks

            new_file = File(filename=filename, file_path=file_path, allocation_method="", size=size)
            db.session.add(new_file)
            db.session.commit()

            allocation_info = allocate_file(new_file.id, size)
            new_file.allocation_method = allocation_info
            db.session.commit()

            allocation_history = AllocationHistory(file_id=new_file.id, allocation_method=allocation_info)
            db.session.add(allocation_history)
            db.session.commit()

            flash(f'File successfully uploaded and allocated using {allocation_info}')
            socketio.emit('file_uploaded', {'id': new_file.id, 'filename': new_file.filename,
                                            'allocation_method': new_file.allocation_method, 'size': new_file.size})
        else:
            flash('File type not allowed')
            return redirect(request.url)
    return redirect(url_for('index'))

@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    file = File.query.get(file_id)
    if file:
        try:
            os.remove(file.file_path)
        except FileNotFoundError:
            pass  # Arquivo já foi removido manualmente ou não existe
        db.session.delete(file)
        db.session.commit()
        flash('File successfully deleted')
        socketio.emit('file_deleted', {'id': file_id})
    else:
        flash('File not found')
    return redirect(url_for('index'))

@app.route('/file/<int:file_id>')
def file_details(file_id):
    file = File.query.get(file_id)
    if file:
        allocation_history = AllocationHistory.query.filter_by(file_id=file_id).all()
        return render_template('file_details.html', file=file, allocation_history=allocation_history)
    else:
        flash('File not found')
        return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('query')
    if query:
        files = File.query.filter(File.filename.contains(query)).all()
    else:
        files = File.query.all()
    return render_template('index.html', files=files)

@app.route('/tag/<string:tag_name>')
def files_by_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    if tag:
        files = tag.files
        return render_template('index.html', files=files)
    else:
        flash(f'No files found with tag {tag_name}')
        return redirect(url_for('index'))

@app.route('/comment', methods=['POST'])
def add_comment():
    file_id = request.form.get('file_id')
    content = request.form.get('content')
    if file_id and content:
        comment = Comment(file_id=file_id, content=content)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully')
        return redirect(url_for('file_details', file_id=file_id))
    else:
        flash('Failed to add comment')
        return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)
