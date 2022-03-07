from flask import Response
from flask_restful import Resource
from models import LikePost, db
import json
from my_decorators import check_ownership_of_post_likes, handle_db_insert_error, is_valid_int_delete, is_valid_int_delete_post_likes, is_valid_int_post_likes, secure_post_likes
from . import can_view_post
import flask_jwt_extended

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    @is_valid_int_post_likes
    @secure_post_likes
    @handle_db_insert_error
    def post(self, post_id):
        # Your code here
        # Creating a new like post to insert
        like_post = LikePost(self.current_user.id, post_id)
        
        db.session.add(like_post)
        db.session.commit()
        return Response(json.dumps(like_post.to_dict()), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    @is_valid_int_delete_post_likes
    @check_ownership_of_post_likes
    def delete(self, post_id, id):
        # Your code here
        LikePost.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Like id={0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/<post_id>/likes', 
        '/api/posts/<post_id>/likes/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/<post_id>/likes/<id>', 
        '/api/posts/<post_id>/likes/<id>/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
