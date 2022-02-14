from flask import Response, request
from flask_restful import Resource
from models import User
from . import get_authorized_user_ids
import json

class SuggestionsListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # Your code here:
        ids_for_me_and_my_friends = get_authorized_user_ids(self.current_user)
        users = User.query.filter(User.id.notin_(ids_for_me_and_my_friends)).limit(7)
        users_list_of_dictionaries = [
            user.to_dict() for user in users
        ]
        return Response(json.dumps(users_list_of_dictionaries), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        SuggestionsListEndpoint, 
        '/api/suggestions', 
        '/api/suggestions/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
