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
            "phone",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "role"]
        read_only_fields = fields


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone"]
        extra_kwargs = {
            "first_name": {"required": False, "allow_blank": True, "max_length": 150},
            "last_name": {"required": False, "allow_blank": True, "max_length": 150},
            "phone": {"required": False, "allow_blank": True, "max_length": 32},
        }

    def validate_phone(self, value):
        value = (value or "").strip()
        if value and not all(char.isdigit() or char in "+-() " for char in value):
            raise serializers.ValidationError("Введите корректный номер телефона.")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        ]

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
        user = User.objects.create_user(password=password, role=User.ROLE_USER, **validated_data)
        return user


class AgentCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "phone"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "phone": {"required": False, "allow_blank": True},
        }

    def validate_email(self, value):
        value = self.Meta.model.objects.normalize_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(
            password=password,
            role=User.ROLE_AGENT,
            **validated_data,
        )


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
