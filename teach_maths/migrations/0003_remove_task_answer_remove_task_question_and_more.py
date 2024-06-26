# Generated by Django 5.0.6 on 2024-06-08 15:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teach_maths", "0002_rename_answers_task_answer_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="task",
            name="answer",
        ),
        migrations.RemoveField(
            model_name="task",
            name="question",
        ),
        migrations.CreateModel(
            name="QuestionAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question", models.TextField()),
                ("answer", models.TextField()),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="teach_maths.task",
                    ),
                ),
            ],
        ),
    ]
