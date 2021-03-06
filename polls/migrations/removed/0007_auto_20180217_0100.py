# Generated by Django 2.0.2 on 2018-02-17 00:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0006_league_userstoleagues'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='id',
            field=models.AutoField(default=99, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='league',
            name='code',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.RemoveField(
            model_name='userstoleagues',
            name='league',
        ),
        migrations.AddField(
            model_name='userstoleagues',
            name='league',
            field=models.ForeignKey(default=99, on_delete=django.db.models.deletion.CASCADE, to='polls.League'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='userstoleagues',
            name='user',
        ),
        migrations.AddField(
            model_name='userstoleagues',
            name='user',
            field=models.ForeignKey(default=99, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
