from flask import Blueprint, current_app, jsonify, render_template, request, send_from_directory

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return send_from_directory(current_app.root_path, 'index.html')


@views.route('/profile/<username>')
def profile(username):
    args = request.args
    name = args.get('name')
    return render_template('profile.html', name=username)


@views.route('/json')
def json():
    return jsonify({'name': 'tim', 'age': 20})
