from db_models.TrainingPlan import TrainingPlan, SegmentDuration


class TestPlan:
    @staticmethod
    async def generate() -> TrainingPlan:
        # Check for saved training plans
        test_plan = await TrainingPlan.filter(name__contains='test plan').first().prefetch_related("segments")

        if not test_plan:
            print('Creating test plan')

            test_plan = await TrainingPlan.create(name="test plan")
            await SegmentDuration.create(name="Warmup", duration=10, resistance=20, training_plan=test_plan)
            await SegmentDuration.create(name="Uphill 1", duration=10, resistance=40, training_plan=test_plan)
            await SegmentDuration.create(name="Downhill 1", duration=10, resistance=30, training_plan=test_plan)
            await SegmentDuration.create(name="Uphill 2", duration=10, resistance=40, training_plan=test_plan)
            await SegmentDuration.create(name="Downhill 2", duration=10, resistance=30, training_plan=test_plan)
            await SegmentDuration.create(name="Cooldown", duration=10, resistance=20, training_plan=test_plan)
            await test_plan.save()

            test_plan = await TrainingPlan.first().prefetch_related("segments")

        for segment in test_plan.segments:
            print(segment)

        return test_plan