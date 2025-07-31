from django.db import migrations


def load_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    Tag.objects.get_or_create(name='Завтрак', slug='breakfast')
    Tag.objects.get_or_create(name='Обед', slug='lunch')
    Tag.objects.get_or_create(name='Ужин', slug='dinner')

class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_load_initial_tags'),  # <- Replace with your latest migration
    ]

    operations = [
        migrations.RunPython(load_tags),
    ]
