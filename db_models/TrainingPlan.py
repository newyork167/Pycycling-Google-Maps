from tortoise.models import Model
from tortoise import fields

class TrainingPlan(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    # segments = fields.ManyToManyField('models.SegmentDuration', related_name='training_plans')
    segments = fields.ReverseRelation["SegmentDuration"]

    def __str__(self):
        return self.name

class SegmentDuration(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    duration = fields.IntField()
    resistance = fields.IntField()

    training_plan: fields.ForeignKeyRelation[TrainingPlan] = fields.ForeignKeyField(
        "models.TrainingPlan", related_name="segments"
    )

    def __str__(self):
        return f"{self.name}: {self.duration=} - {self.resistance=}"
