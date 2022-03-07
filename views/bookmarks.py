from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db
import json
from . import can_view_post
from my_decorators import handle_db_insert_error, secure_bookmark, check_ownership_of_bookmark, is_valid_int, is_valid_int_delete
import flask_jwt_extended

# all of views folder are our rest endpoints
# we use flask_restful, which is a flask library that helps us organize our endpoints
# each endpoint has a list view and a detail view



class BookmarksListEndpoint(Resource):
# List will list all of the existing bookmarks and is where you create new ones

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def get(self):
        # Your code here
        # Goal is to only show the bookmarks that are associated with
        # the current user. Approach:
        #   1. Use SQL Alchemy to execute the query
        #       using the "Bookmark" model from the models folder
        #   2. When we return this list, it's serialized using JSON.

        bookmarks = Bookmark.query.filter_by(user_id=self.current_user.id).order_by('id').all()
        # print(bookmarks)

        # Convert list of bookmark models to a list of dictionaries:
        bookmark_list_of_dictionaries = [
            bookmark.to_dict() for bookmark in bookmarks
        ]
        return Response(json.dumps(bookmark_list_of_dictionaries), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    @is_valid_int # ordering explanation on doc
    # Handles trying to bookmark stuff you can't see own/follow
    @secure_bookmark
    # Handles trying to bookmark the same post twice, constraint error
    # in models
    @handle_db_insert_error
    def post(self):
        # Your code here
        # Goal:
        #   1. Get the post_id from the request body
        #   2. Check that the user is authorized to bookmark the post
        #   3. Check that the post_id exists and is valid
        #   4. If 1, 2, 3: insert into the database
        #   5. Return the new bookmarked post (and the bookmark id)
        #       to the user as part of the response
        
        # This is the data that the user sent us
        body = request.get_json()
        # print(body)
        post_id = body.get('post_id')
        
        # to create a Bookmark, you need to pass it a user_id and a post_id
        bookmark = Bookmark(self.current_user.id, post_id)
        # these two lines save ("commit") the new record to the database:
        db.session.add(bookmark)
        db.session.commit()
        
        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)

class BookmarkDetailEndpoint(Resource):
# Detail is for PATCH (updating), GET (individual bookmarks), DELETE individual bookmark
# Also creating new bookmarks

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    @is_valid_int_delete
    # Check ownership, can't delete if it's not in yours
    @check_ownership_of_bookmark
    def delete(self, id):
        # Your code here
        # bookmark = Bookmark.query.get(id)
        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Bookmark {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)

def initialize_routes(api):
    # this is saying that both those endpoints with / and ' '
    # refer to the BookmarksListEndpoint class
    # also list class always has access to who is logged into the system
    # so in the last line with current user, we are only returning bookmarks that
    # are flagged by the current user

    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<id>', 
        '/api/bookmarks/<id>',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
