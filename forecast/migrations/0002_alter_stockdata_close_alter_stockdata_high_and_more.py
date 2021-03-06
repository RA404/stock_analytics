# Generated by Django 4.0.6 on 2022-07-05 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockdata',
            name='close',
            field=models.DecimalField(decimal_places=10, max_digits=21),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='high',
            field=models.DecimalField(decimal_places=10, max_digits=21),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='low',
            field=models.DecimalField(decimal_places=10, max_digits=21),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='open',
            field=models.DecimalField(decimal_places=10, max_digits=21),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='volume',
            field=models.DecimalField(decimal_places=10, max_digits=21),
        ),
        migrations.AlterUniqueTogether(
            name='stockdata',
            unique_together={('ticket', 'period', 'date', 'time')},
        ),
    ]
