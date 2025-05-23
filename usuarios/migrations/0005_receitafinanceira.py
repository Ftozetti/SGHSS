# Generated by Django 5.2 on 2025-05-11 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_resultadoexame_imagem'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceitaFinanceira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('procedimento', models.CharField(choices=[('consulta', 'Consulta Presencial'), ('teleconsulta', 'Teleconsulta'), ('exame', 'Exame')], max_length=20)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=8)),
                ('data', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
