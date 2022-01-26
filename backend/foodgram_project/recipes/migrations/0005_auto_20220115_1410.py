# Generated by Django 2.2.16 on 2022-01-15 14:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20220115_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags_in_recipe', to='recipes.Recipe'),
        ),
    ]
