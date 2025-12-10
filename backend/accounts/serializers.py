from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "role",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "role": {"required": False, "default": User.ROLE_USER},
        }

    def validate_email(self, value):
        value = self.Meta.model.objects.normalize_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError({"non_field_errors": ["Пароль и подтверждение пароля не совпадают."]})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm", None)
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        request = self.context.get("request")
        email = User.objects.normalize_email(attrs.get("email"))
        password = attrs.get("password")
        user = authenticate(request=request, username=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Неверный email или пароль"})
        if not user.is_active:
            raise serializers.ValidationError({"detail": "Учетная запись не активна"})
        attrs["user"] = user
        tokens = TokenObtainPairSerializer.get_token(user)
        attrs["refresh"] = str(tokens)
        attrs["access"] = str(tokens.access_token)
        return attrs

    class Meta:
        model = User
