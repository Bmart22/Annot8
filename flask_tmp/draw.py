import os
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, jsonify, send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from base64 import b64encode

from flask_tmp.auth import login_required
from flask_tmp.db import get_db
#from flask import current_app

bp = Blueprint('draw', __name__)


@bp.route('/new_image', methods=('GET', 'POST'))
def new_image():

    if request.method == 'POST':
        if g.user:
            user = g.user["id"]
        else:
            user = "scratch"
        
        image = request.files['image']
        filename = secure_filename(image.filename)
        
        # increment image name if it has already been uploaded
        existing_images = os.listdir(current_app.config['UPLOAD_FOLDER'])
        name, type = filename.split(".")
        ind = 0
        flag = True
        while flag:
            if filename in existing_images:
                ind += 1
                filename = name + f"_{ind}." + type
            else:
                flag = False
        
        # Insert a new image into the database
        db = get_db()
        db.execute(
            'INSERT INTO annotations (title, image, author_id)'
            ' VALUES (?, ?, ?)',
            ("img", filename, user)
        )
        db.commit()
        
        image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        # Get the id of the newly created image
        last_record = get_db().execute(
            'SELECT id'
            ' FROM annotations'
            ' ORDER BY created DESC LIMIT 1',
        ).fetchone()
        
        # Redirect to the creation page
        return redirect(url_for('draw.create', id=last_record['id']))
    

@bp.route('/<int:id>/create', methods=('GET', 'POST'))
def create(id):
    
    # Save coordinates
    if request.method == 'POST':
        coors = request.get_json() #json automatically loaded as python dictionary
        coors = json.dumps(coors) #Convert to json string
        
        db = get_db()
        db.execute(
            'UPDATE annotations SET coordinates = ?'
            ' WHERE id = ?',
            (coors, id)
        )
        db.commit()
        
        return
    
    # Display the creation page
    if request.method == 'GET':
#        if g.user:
        last_record = get_db().execute(
            'SELECT image'
            ' FROM annotations a'
            ' WHERE a.id = ?',
            (id,)
        ).fetchone()
        
        return render_template('draw/create.html', img_id=id, image= last_record['image'])


@bp.route('/<int:id>/coors', methods=('GET', 'POST'))
def loadData(id):

    if request.method == 'GET':
        coors = get_db().execute(
            'SELECT coordinates'
            ' FROM annotations a JOIN user u ON a.author_id = u.id'
            ' WHERE a.id = ?',
            (id,)
        ).fetchone()
    
    return jsonify( coors['coordinates'] )
    
@bp.route('/<path:filename>/image', methods=('GET', 'POST'))
def loadImage(filename):
    print(current_app.config['UPLOAD_FOLDER'])
    return send_from_directory( current_app.config['UPLOAD_FOLDER'], filename )

@bp.route('/gallery', methods=('GET', 'POST'))
def index():
#    images = []
    if request.method == 'GET':
        # If user is logged in
        if g.user:
            images = get_db().execute(
                'SELECT id, title, image'
                ' FROM annotations'
                ' WHERE author_id = ?',
                (g.user['id'],)
            ).fetchall()
            
            return render_template('draw/index.html', images=images[::-1])
        else:
            return render_template('draw/index.html', images=[])
    
    # When user asks to create a new image
    if request.method == 'POST':
        return redirect(url_for('draw.new_image'), code=307)
    
    
# Landing page
@bp.route('/', methods=('GET', 'POST'))
def landing():
    return render_template('draw/landing.html')
        
        
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
#    get_post(id)
    db = get_db()
    db.execute('DELETE FROM annotations WHERE id = ?', (id,))
    db.commit()
    return
#    return redirect(url_for('blog.index'))
    

