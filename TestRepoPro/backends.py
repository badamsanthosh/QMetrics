from django.conf import Settings
from django.contrib.auth.models import check_password
from TestRepoPro.models import User
import logging
log = logging.getLogger(__name__)

class EmailAuthBackend( object ):
    """
    A custom authentication back end . Allows user to login using email id.
    """
    def authenticate(self, email = None, password = None ):
        try:
            user = User.objects.get( email = email )            
            if user.check_password( password ):            
                return user
            
        except User.DoesNotExist:
            return None
        
    def get_user(self, user_id ):
        try:
            user = User.objects.get( pk = user_id )
            return user
            if user.is_active():
                return user
            return None
        
        except User.DoesNotExist:
            return None