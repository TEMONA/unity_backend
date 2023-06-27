from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
import uuid
from datetime import datetime, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    kaonavi_code = models.CharField(max_length=10, unique=True)
    chatwork_id = models.CharField(max_length=50, unique=True, null=True)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class UserActivateTokensManager(models.Manager):

    def activate_user_by_token(self, activate_token):
        user_activate_token = self.filter(
            activate_token=activate_token,
            expired_at__gte=datetime.now() # __gte = greater than equal
        ).first()
        if hasattr(user_activate_token, 'user'):
            user = user_activate_token.user
            user.is_active = True
            user.save()
            return user


class UserActivateTokens(models.Model):

    token_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activate_token = models.UUIDField(default=uuid.uuid4)
    expired_at = models.DateTimeField()

    objects = UserActivateTokensManager()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def publish_activate_token(sender, instance, **kwargs):
    if not instance.is_active:
        user_activate_token = UserActivateTokens.objects.create(
            user=instance,
            expired_at=datetime.now()+timedelta(days=settings.ACTIVATION_EXPIRED_DAYS),
        )
        subject = 'Please Activate Your Account'
        message = f'URLにアクセスしてアカウント登録を完了してください。\n {settings.MY_URL}/api/users/{user_activate_token.token_id}'
    if instance.is_active:
        subject = 'Activated! Your Account!'
        message = 'ユーザーが使用できるようになりました'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [
        instance.email,
    ]
    send_mail(subject, message, from_email, recipient_list)

def top_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['images', 'top_image', f'{instance.user.id}{instance.nickname}.{ext}'])


class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE, related_name='profile')

    """ Profile Fields """
    top_image = models.ImageField(
        verbose_name="トップ画像", upload_to=top_image_upload_path, blank=True, null=True)
    nickname = models.CharField(verbose_name="ニックネーム", max_length=20)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

    """ Environment """
    LOCATION = [
        ('hokkaido', '北海道'),
        ('tohoku', '東北'),
        ('kanto', '関東'),
        ('hokuriku', '北陸'),
        ('chubu', '中部'),
        ('kansai', '関西'),
        ('chugoku', '中国'),
        ('shikoku', '四国'),
        ('kyushu', '九州'),
    ]
    location = models.CharField(verbose_name="出身地", max_length=32, choices=LOCATION, blank=True, null=True)

    """ Appealing Point """
    hobby = models.CharField(
        verbose_name="趣味", max_length=32, blank=True, null=True)
    tweet = models.CharField(verbose_name="一言", max_length=10, blank=True, null=True)
    introduction = models.TextField(verbose_name="自己紹介", max_length=1000, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def from_last_login(self):
        now_aware = datetime.now().astimezone()
        if self.user.last_login is None:
            return "ログイン歴なし"
        login_time: datetime = self.user.last_login
        if now_aware <= login_time + timedelta(days=1):
            return "24時間以内"
        elif now_aware <= login_time + timedelta(days=2):
            return "2日以内"
        elif now_aware <= login_time + timedelta(days=3):
            return "3日以内"
        elif now_aware <= login_time + timedelta(days=7):
            return "1週間以内"
        else:
            return "1週間以上"

    def __str__(self):
        return self.nickname

class LunchRequests(models.Model):

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipient_calender_uid = models.CharField(max_length=255)
    apply_content = models.CharField(max_length=255)
    preferred_days = models.JSONField()
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.applicant) + ' --- send to ---> ' + str(self.recipient_calender_uid)
