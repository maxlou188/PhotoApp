from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json
import flask_jwt_extended

from my_decorators import check_ownership_of_following, handle_db_insert_error, is_valid_int_delete, is_valid_int_following, secure_following

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def get(self):
        # Your code here
        followings = Following.query.filter_by(user_id=self.current_user.id).all()
        following_list_of_dictionaries = [
            following.to_dict_following() for following in followings
        ]

        return Response(json.dumps(following_list_of_dictionaries), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    @is_valid_int_following
    @secure_following
    @handle_db_insert_error
    def post(self):
        # Your code here
        # Get the request, returns the dictionary
        # get the requested dude to follow
        body = request.get_json()
        following_id = body.get('user_id')
        # Create the new following class
        # and add it to the database
        new_following = Following(self.current_user.id, following_id)
        
        db.session.add(new_following)
        db.session.commit()
        return Response(json.dumps(new_following.to_dict_following()), mimetype="application/json", status=201)


class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    @is_valid_int_delete
    @check_ownership_of_following
    def delete(self, id):
        # Your code here
        Following.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message' : 'Successfully unfollowed user {0}'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<id>', 
        '/api/following/<id>/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
