from flask import render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user

from app import app, db
from app.models import Entry
from app import auth

@app.route('/')
@app.route('/index')
def index():
    entries = Entry.query.all()
    return render_template('index.html', entries=entries)

@app.route('/tambah')
def lempar():
    return redirect(url_for('add'))

@app.route('/add', methods=['POST', 'GET'])
@login_required
def add():
    if not current_user.is_admin:
        flash("CRUD hanya bisa dilakukan oleh Admin")
        return redirect(url_for('index'))
    if not current_user.is_editor:
        flash("Anda hanya bisa melakukan Update data saja")
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        if title != '' or description != '':
            entry = Entry(title=title, description=description)
            db.session.add(entry)
            db.session.commit()
            return redirect('/')
        else:
            flash("Form wajib isi")
            return redirect('/')
    return render_template('add.html', title='Add Item')

@app.route('/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update(id):
    if not current_user.is_admin and not current_user.is_editor:
        flash("User biasa tidak CRUD")
        return redirect(url_for('index'))
    entry = Entry.query.get(id)
    if entry:
        if request.method == 'POST':
            entry.title = request.form['title']
            entry.description = request.form['description']
            db.session.commit()
            return redirect('/')
        return render_template('update.html', entry=entry, title='Update')
    
    return "Update Data"

def confirm_delete(entry):
    if request.method == 'POST':
        db.session.delete(entry)
        db.session.commit()
        flash("Data Deleted!")
        return redirect('/')
    return render_template('confirm_delete.html', entry=entry, title='Delete')

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    if not current_user.is_admin or not current_user.is_editor:
        flash("Hanya admin yang bisa menghapus data!")
        return redirect(url_for('index'))
    if not id or id != 0:
        entry = Entry.query.get(id)
        if entry:
            return confirm_delete(entry)
                
    return "Delete Data"
