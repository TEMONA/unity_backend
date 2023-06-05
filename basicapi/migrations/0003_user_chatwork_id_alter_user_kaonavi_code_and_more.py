# Generated by Django 4.0.2 on 2023-06-03 08:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('basicapi', '0002_user_kaonavi_code_alter_user_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='chatwork_id',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='kaonavi_code',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255),
        ),
        migrations.CreateModel(
            name='UserActivateTokens',
            fields=[
                ('token_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('activate_token', models.UUIDField(default=uuid.uuid4)),
                ('expired_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]