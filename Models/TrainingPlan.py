from tortoise.models import Model
from tortoise import fields

class TrainingPlan(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    segments = fields.ManyToManyField('models.Segment', related_name='training_plans')

class SegmentDuration(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    duration = fields.IntField()
    resistance = fields.IntField()
