from datetime import datetime
from . import db

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    __table_args__ = (
        # This right here says that in the DB there is a unique 
        # user id and post id, doesn't allow duplicates
        db.UniqueConstraint('user_id', 'post_id'),
    )

    # These variables correspond to the columns in the bookmarks table
    # SELECT * FROM bookmarks WHERE user_id = 12
    # Matching a table like that

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'),
        nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='cascade'),
        nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

    # read-only property for referencing User properties
    # This queries the post table
    # bookmark model.post will query the posts table for the information 
    # that we actually want corresponding to the post_id
    # because right now all we have is the post_id

    # Model folder querys the database
    # Views folder acts as a middle man and returns what you want to return

    post = db.relationship('Post', backref="bookmarks", lazy=False)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

    def to_dict(self):
        return {
            'id': self.id,
            'post': self.post.to_dict(include_comments=False)
        }

    def __repr__(self):
        return '<Bookmark %r>' % self.id       
