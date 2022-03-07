from flask import (
    jsonify, request, make_response, render_template, redirect
)
from models import User
import flask_jwt_extended



def logout():
    # redirect to the home page
    resp = make_response(redirect('/login', 302))
    # get rid of the cookies
    flask_jwt_extended.unset_jwt_cookies(resp)
    return resp

def login():
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')
       
        if not username:
            return render_template(
                'login.html', 
                message='Missing username'
            )
        if not password:
            return render_template(
                'login.html', 
                message='Missing password'
            )
        # proceed with database check
        user = User.query.filter_by(username=username).one_or_none()
        print(user)

        if user:
            #check password
            if user.check_password(password):
                print('the user is authenticated')
                access_token = flask_jwt_extended.create_access_token(identity=user.id)
                # Set the JWT cookies in response before returning it to the user
                # Encoding the user's ID in the JWT
                response = make_response(redirect('/'))
                flask_jwt_extended.set_access_cookies(response, access_token)
                return response
            else:
                return render_template(
                    'login.html', 
                    message='Wrong password'
                )   
        # authenticate user here. If the user sent valid credentials, set the
        # JWT cookies:
        # https://flask-jwt-extended.readthedocs.io/en/3.0.0_release/tokens_in_cookies/
        else:
            return render_template(
                    'login.html', 
                    message='Username not in database'
            )
    else:
        return render_template(
            'login.html'
        )

def initialize_routes(app):
    app.add_url_rule('/login', 
        view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=logout)