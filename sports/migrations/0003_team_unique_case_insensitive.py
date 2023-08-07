import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sports', '0002_roster_relations_and_indexes'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='team',
            name='unique_team_city_mascot',
        ),
        migrations.AddConstraint(
            model_name='team',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('city'),
                django.db.models.functions.text.Lower('mascot'),
                name='unique_team_city_mascot_ci',
                violation_error_message='A team with this city and mascot already exists.',
            ),
        ),
    ]
