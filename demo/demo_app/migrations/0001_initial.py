# Generated by Django 4.2.8 on 2024-01-01 08:31

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Helpful text', max_length=256, verbose_name='name')),
                ('slug', models.SlugField(help_text='Helpful text', verbose_name='slug')),
                ('url', models.URLField(help_text='Helpful text', verbose_name='url')),
                ('email', models.EmailField(help_text='Helpful text', max_length=254, verbose_name='email')),
                ('birthday', models.DateField(help_text='Helpful text', verbose_name='birthday')),
                ('friends', models.ManyToManyField(blank=True, help_text='Helpful text', to='demo_app.person')),
            ],
            options={
                'verbose_name': 'person',
                'verbose_name_plural': 'people',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_and_time', models.DateTimeField(help_text='Helpful text', verbose_name='date and time')),
                ('picture', models.ImageField(help_text='Helpful text', upload_to='pictures', verbose_name='picture')),
                ('is_color', models.BooleanField(default=True, help_text='Helpful text', verbose_name='color')),
                ('person', models.ForeignKey(help_text='Helpful text', on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='demo_app.person')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'picture',
                'verbose_name_plural': 'pictures',
                'ordering': ('-date_and_time',),
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(help_text='Helpful text', on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='demo_app.person')),
                ('picture', models.ForeignKey(help_text='Helpful text', on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='demo_app.picture')),
            ],
            options={
                'verbose_name': 'favorite',
                'verbose_name_plural': 'favorites',
            },
        ),
    ]