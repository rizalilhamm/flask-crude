import re
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from app import views
from app.models import User

def validate_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if not (re.search(regex, email)):
        flash("Invalid Email Format")
        return False
    return True


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Currently you are logging in')
        return redirect(url_for('index'))

    if request.method == "POST":
        email = request.form.get('email')
        if validate_email(email) is False:
            return redirect(url_for('login'))
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first() or User.query.filter_by(name=email).first()

        if not user or not user.check_password(password):
            flash("Invalid Email or Password")
            return redirect(url_for('login'))
      
        if user.is_admin == True:
            flash("Anda login sebagai admin.")
      
        elif user.is_editor:
            flash("Anda login sebagai User Editor")
      
        else:
            flash("Anda Login sebagai user biasa")        
      
        login_user(user)
        next_page = request.args.get('next')
      
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        if validate_email(email) is False:
            return redirect(url_for('register'))
            
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')
        user = User.query.filter_by(email=email).first()
        
        if user is not None:
            flash("Email Sudah terdaftar silahkan coba login")
            return redirect(url_for('register'))
        elif password != confirm_password:
            flash("Password harus sama")
            return redirect(url_for('register'))
        new_user = User(name=name, email=email, password=password)
        new_user.hash_password()
        
        if user_type.lower() == 'admin' :
            new_user.is_admin, new_user.is_editor = True, True
        elif user_type.lower() == 'editor':
            new_user.is_editor = True

        if new_user.is_admin:
            flash("Selamat, anda terdaftar sebagai Admin")
        elif new_user.is_editor:
            flash("Selamat, anda terdaftar sebagai Editor")
        else:
            flash("Anda terdaftar sebagai User biasa")

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', title='Register')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda sudah Keluar!')
    return redirect(url_for('login'))
