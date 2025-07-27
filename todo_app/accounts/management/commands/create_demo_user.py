"""
Optimized Django management command for fast demo user creation
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from todos.models import Category, Task, Priority, Status
from django.db import transaction


class Command(BaseCommand):
    help = 'Create demo user with sample data (optimized for fast startup)'
    
    def add_arguments(self, parser):
        parser.add_argument('--skip-sample-data', action='store_true', 
                          help='Only create user, skip sample tasks')

    @transaction.atomic
    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        skip_sample = options.get('skip_sample_data', False)
        
        username = 'demo_user'
        password = 'demo123456'
        email = 'demo@example.com'

        # Fast user creation/update
        try:
            user = User.objects.get(username=username)
            if verbosity > 0:
                self.stdout.write(f"Demo user exists: {username}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True,
                first_name='Demo',
                last_name='User'
            )
            if verbosity > 0:
                self.stdout.write(f"Created demo user: {username}")

        # Always ensure password is correct
        user.set_password(password)
        user.is_active = True
        user.save()

        # Skip sample data creation if requested or if data already exists
        if skip_sample or Task.objects.filter(user=user).exists():
            if verbosity > 0:
                self.stdout.write("Skipping sample data creation")
            return

        # Fast sample data creation
        self._create_minimal_sample_data(user, verbosity)

    def _create_minimal_sample_data(self, user, verbosity):
        """Create minimal sample data for demo purposes"""
        now = timezone.now()
        
        # Create minimal categories
        categories = []
        cat_names = ['Work', 'Personal', 'Learning']
        
        for name in cat_names:
            cat, created = Category.objects.get_or_create(
                title=name, 
                user=user,
                defaults={'title': name}
            )
            categories.append(cat)

        # Create minimal sample tasks
        tasks_data = [
            {
                'title': 'Complete Django Documentation',
                'category': categories[0],
                'priority': Priority.HIGH,
                'status': Status.PROGRESS,
                'progress': 75,
                'start_date': now - timedelta(days=2),
                'due_date': now + timedelta(days=1),
                'description': 'Finish Django app documentation'
            },
            {
                'title': 'Plan Weekend Activities',
                'category': categories[1],
                'priority': Priority.LOW,
                'status': Status.NOT_COMPLETED,
                'progress': 0,
                'start_date': now,
                'due_date': now + timedelta(days=3),
                'description': 'Plan activities for the weekend'
            },
            {
                'title': 'Learn React Basics',
                'category': categories[2],
                'priority': Priority.MIDDLE,
                'status': Status.COMPLETED,
                'progress': 100,
                'start_date': now - timedelta(days=7),
                'due_date': now - timedelta(days=1),
                'description': 'Complete React fundamentals course'
            },
        ]

        # Bulk create tasks for better performance
        tasks_to_create = [
            Task(user=user, **task_data) for task_data in tasks_data
        ]
        Task.objects.bulk_create(tasks_to_create, ignore_conflicts=True)

        if verbosity > 0:
            self.stdout.write(f"Created {len(tasks_data)} sample tasks")
            self.stdout.write("Demo user setup complete")