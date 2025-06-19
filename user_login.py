from flask_login import UserMixin

class UserLogin(UserMixin):
    def from_db(self, user_id, db):
        self.__user = db.get_user_by_id(user_id)
        return self
    
    def create(self, user):
        self.__user = user
        return self
    
    def get_email(self):
        return str(self.__user['email'])
    
    def get_id(self):
        return self.__user['id']
    
    def get_avatar(self):
        if self.__user['avatar']:
            return self.__user['avatar']
        else:
            return False
        
    def get_class(self):
            return self.__user['class']

    def get_self(self):
        return self.__user
    
    def verify_avatar_ext(self, filename):
        return True if filename.rsplit('.', 1)[1] in ('png', 'jpg', 'jpeg') else False

    
        