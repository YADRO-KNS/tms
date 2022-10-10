from django.contrib.auth import get_user_model
from rest_framework.serializers import HyperlinkedIdentityField, ModelSerializer
from users.models import Group

UserModel = get_user_model()


class GroupSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:group-detail')

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', 'url')


class UserSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:v1:user-detail')

    class Meta:
        model = UserModel
        fields = (
            'id', 'url', 'username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_active',
            'date_joined',
        )

        read_only_fields = ('date_joined',)
        extra_kwargs = {
            'password': {'write_only': True}
        }
