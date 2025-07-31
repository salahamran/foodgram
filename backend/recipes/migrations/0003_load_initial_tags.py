from django.db import migrations


def create_initial_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    Tag.objects.get_or_create(name='Завтрак', slug='breakfast')
    Tag.objects.get_or_create(name='Обед', slug='lunch')
    Tag.objects.get_or_create(name='Ужин', slug='dinner')

class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),  # replace with actual previous migration file
    ]

    operations = [
        migrations.RunPython(create_initial_tags),
    ]
