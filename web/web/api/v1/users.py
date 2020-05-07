from web import app

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy 

from web.models.user import User 

@app.route('/api/v1/users', methods=['GET'])
def get_user_ids():
    pass

@app.route('/api/v1/user/<string:user_id>', methods=['GET'])
def show_user_info(user_id):
    pass

@app.route('api/v1/user/<string:user_id>', methods=['PUT'])
def modify_user(user_id):
    pass

@app.route('api/v1/user', methods=['POST'])
def add_user():
    pass