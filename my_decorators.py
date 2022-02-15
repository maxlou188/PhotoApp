from datetime import datetime
import json
from flask import Response, request
from views import can_view_post, get_authorized_user_ids
from models import Bookmark, Comment, Following, LikePost, User

# # Decorator Format:
# # https://realpython.com/primer-on-python-decorators/
# Decorator is do something real quick and then execute the function
# Example 4, want to do something before print hi and after print hi
# like wrapping the function in another function
# Example 5 has the better syntax -
#   if you put the @decorator before any function definition,
#   it will wrap the function in the decorator, calls it before
#   and after any time the function is called

# #########################################
# # Example 1: Functions can be arguments #
# #########################################
# # Say you have two greetings and you want a 
# # convenient way to use either:

# def greeting1(name):
#     return f"Hello {name}"

# def greeting2(name):
#     return f"What up {name}"

# def greet(greeter_func, name):
#     print(greeter_func(name))

# greet(greeting1, 'Bob')
# greet(greeting2, 'Maria')


# ###########################################
# # Example 2: Functions can be defined and # 
# # invoked inside of other functions.      #
# ###########################################
# def parent():
#     print("Printing from the parent() function")

#     def first_child():
#         print("Printing from the first_child() function")

#     def second_child():
#         print("Printing from the second_child() function")

#     second_child()
#     first_child()

# parent()


# ###############################
# # Example 3: Functions can be # 
# # returned and invoked later. #
# ###############################
# def parent(num):
#     def first_child():
#         return "Hi, I am Emma"

#     def second_child():
#         return "Call me Liam"

#     if num == 1:
#         return first_child
#     else:
#         return second_child

# f1 = parent(1)
# f2 = parent(2)

# print(f1)
# print(f2)
# print(f1())
# print(f2())

# ###################################
# # Example 4: Your First Decorator #
# ###################################
# '''
# * A decorator takes a function as an argument, 
#   and then wraps some functionality around it.
# * Useful for error checking and security
# '''
# def my_decorator(func):
#     def wrapper():
#         print("Something is happening before the function is called.")
#         func()
#         print("Something is happening after the function is called.")
#     return wrapper

# def say_hi():
#     print('Hi')

# def say_bye():
#     print('Bye')

# say_hi_plus_extras = my_decorator(say_hi)
# say_bye_plus_extras = my_decorator(say_bye)

# print(say_hi_plus_extras)
# print(say_bye_plus_extras)
# say_hi_plus_extras()
# say_bye_plus_extras()


# ################################
# # Example 5: "Syntactic Sugar" #
# ################################
# def my_decorator(func):
#     def wrapper():
#         print("Something is happening before the function is called.")
#         func()
#         print("Something is happening after the function is called.")
#     return wrapper

# @my_decorator
# def say_hi():
#     print('Hi')

# @my_decorator
# def say_bye():
#     print('Bye')

# print(say_hi)
# print(say_bye)
# say_hi()
# say_bye()


# ############################
# # Example 6: args & kwargs #
# ############################
# '''
# Sometimes you want to use a decorator but you don't know 
# how many arguments the inner function will have. If this
# is the case, you can use "args" and "kwargs".

# * args hold a list of any positional parameters
# * kwargs hold a dictionary of any keyword parameters.

# Using this strategy, you can apply your decorator to
# multiple functions with different function signatures. 
# '''
# def security(func):
#     def wrapper(username, *args, **kwargs):
#         if username == 'sjv':
#             # pass all of the arguments to the inner function
#             func(username, *args, **kwargs)
#         else:
#             print('Unauthorized')
#     return wrapper

# @security
# def query_users(username, limit=5, order_by='last_name'):
#     print('filter criteria:', username, limit, order_by)

# @security
# def query_posts(username, before_date=datetime.now()):
#     print('filter criteria:', username, before_date)

# print('\nquerying users table...')
# query_users('sjv', limit=10)

# print('\nquerying posts table...')
# query_posts('hjv4599')


# #######################################
# # Example 7: Flask + SQL Alchemy Demo #
# #######################################
# def id_is_integer_or_400_error(func):
#     def wrapper(self, id, *args, **kwargs):
#         try:
#             int(id)
#             return func(self, id, *args, **kwargs)
#         except:
#             return Response(
#                 json.dumps({'message': '{0} must be an integer.'.format(id)}), 
#                 mimetype="application/json", 
#                 status=400
#             )
#     return wrapper

def handle_db_insert_error(endpoint_function):
    # We are actualy returning the outer_function here
    # if the inner one is not successful
    def outer_function(self, *args, **kwargs):
        try:
            # Try to execute endpoint function and if it is successful,
            # what we will be returning is the endpoint_function's return
            return endpoint_function(self, *args, **kwargs)
        except:
            import sys
            db_message = str(sys.exc_info()[1]) # stores DB error message
            print(db_message)                   # logs it to the console
            message = 'DECORATOR! Database Insert error. Make sure your post data is valid.'
            post_data = request.get_json()
            post_data['user_id'] = self.current_user.id
            response_obj = {
                'message': message, 
                'db_message': db_message,
                'post_data': post_data
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)
    return outer_function

# This function checks if the current user has permissions to bookmark this post
# returns error if you can't gracefully
def secure_bookmark(endpoint_function):
    def outer_function_with_security_checks(self):
        # print('about to issue the post endpoint function...')
        # For can_view_post, we need the post_id of the post we are trying to bookmark
        # and current user to see his permissions
        # body is what we send to the DB, returns that dictionary in the doc
        body = request.get_json()
        post_id = body['post_id']
        # print(post_id)
        print(can_view_post(post_id, self.current_user))
        if can_view_post(post_id, self.current_user):
            return endpoint_function(self)
        else:
            response_obj = {
                'message': "You don't have access to post_id = {0}".format(post_id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
    return outer_function_with_security_checks

def secure_post_likes(endpoint_function):
    def outer_function_with_security_checks(self, post_id):
        # print(can_view_post(post_id, self.current_user))
        if can_view_post(post_id, self.current_user):
            return endpoint_function(self, post_id)
        else:
            response_obj = {
                'message': "You don't have access to post_id = {0}".format(post_id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
    return outer_function_with_security_checks

#bookmark delete
def check_ownership_of_bookmark(endpoint_function):
    def outer_function_with_security_checks(self, id):
        # Delete takes an id, so this is how our inner function knows 
        # that its using the parameters
        # print(id)
        bookmark = Bookmark.query.get(id)
        if bookmark and bookmark.user_id == self.current_user.id:
            return endpoint_function(self, id)
        else:
            response_obj = {
                'message': "You did not create bookmark id={0}".format(id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
    return outer_function_with_security_checks

def check_ownership_of_comment(endpoint_function):
    def outer_function_with_security_checks(self, id):
        comment = Comment.query.get(id)
        if comment and comment.user_id == self.current_user.id:
            return endpoint_function(self, id)
        else:
            response_obj = {
                'message': "You did not create comment id={0}".format(id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
    return outer_function_with_security_checks

def check_ownership_of_following(endpoint_function):
    def outer_function_with_security_checks(self, id):
        following = Following.query.get(id)
        if following and following.user_id == self.current_user.id:
            return endpoint_function(self, id)
        else:
            response_obj = {
                'message': "You did not create follow id={0}".format(id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
    return outer_function_with_security_checks

def secure_following(endpoint_function):
    def outer_function_with_security_checks(self):
        # print('about to issue the post endpoint function...')
        # For can_view_post, we need the post_id of the post we are trying to bookmark
        # and current user to see his permissions
        # body is what we send to the DB, returns that dictionary in the doc
        body = request.get_json()
        user_id = body['user_id']
        following = User.query.get(user_id)
        # print(user_id in get_authorized_user_ids(self.current_user))
        if following:
            return endpoint_function(self)
        else:
            response_obj = {
                'message': "Invalid user_id = {0}".format(user_id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
    return outer_function_with_security_checks

#bookmark post, comment post
def is_valid_int(endpoint_function):
    def outer_function_with_security_checks(self):
        try:
            body = request.get_json()
            post_id = body.get('post_id')
            post_id = int(post_id)
        except:
            response_obj = {
                'message': "Invalid post_id={0}".format(post_id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)
        return endpoint_function(self)
    return outer_function_with_security_checks

def is_valid_int_following(endpoint_function):
    def outer_function_with_security_checks(self):
        try:
            body = request.get_json()
            user_id = body.get('user_id')
            user_id = int(user_id)
        except:
            response_obj = {
                'message': "Invalid user_id={0}".format(user_id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)
        return endpoint_function(self)
    return outer_function_with_security_checks

# bookmark delete, comment delete
def is_valid_int_delete(endpoint_function):
    def outer_function_with_security_checks(self, id):
        try:
            id = int(id)
        except:
            response_obj = {
                'message': "Invalid id={0}".format(id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)
        return endpoint_function(self, id)
    return outer_function_with_security_checks

# post_likes delete
def is_valid_int_delete_post_likes(endpoint_function):
    def outer_function_with_security_checks(self, post_id, id):
        try:
            id = int(id)
        except:
            response_obj = {
                'message': "Invalid id={0}".format(id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)
        return endpoint_function(self, post_id, id)
    return outer_function_with_security_checks

# post_likes post
def is_valid_int_post_likes(endpoint_function):
    def outer_function_with_security_checks(self, post_id):
        print(post_id)
        try:
            post_id = int(post_id)
        except:
            response_obj = {
                'message': "Invalid id={0}".format(post_id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)
        return endpoint_function(self, post_id)
    return outer_function_with_security_checks

def check_ownership_of_post_likes(endpoint_function):
    def outer_function_with_security_checks(self, post_id, id):
        like_post = LikePost.query.get(id)
        if like_post and like_post.user_id == self.current_user.id:
            return endpoint_function(self, post_id, id)
        else:
            response_obj = {
                'message': "You did not like id={0}".format(id) 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
    return outer_function_with_security_checks

#comment post
def is_missing_text(endpoint_function):
    def outer_function_with_security_checks(self):
        body = request.get_json()
        if body.get('text'):
            return endpoint_function(self)
        else:
            response_obj = {
                'message': "Comment post missing text" 
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)
    return outer_function_with_security_checks

# POSTS
# patch
