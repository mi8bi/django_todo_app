"""
Django management command to create demo user with sample data
Place this file at: todo_app/accounts/management/commands/create_demo_user.py
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from todos.models import Category, Task, Priority, Status


class Command(BaseCommand):
    help = 'Create demo user with sample tasks and categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='demo_user',
            help='Username for demo user (default: demo_user)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='demo123456',
            help='Password for demo user (default: demo123456)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='demo@example.com',
            help='Email for demo user (default: demo@example.com)',
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        self.stdout.write(f"Creating/checking demo user: {username}")

        # Create or get demo user
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"Demo user already exists: {username}")

            # Always reset password to ensure it's correct
            user.set_password(password)
            user.is_active = True
            user.email = email
            user.save()
            self.stdout.write("Updated demo user password and settings")

        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True,
                first_name='Demo',
                last_name='User'
            )
            self.stdout.write(f"Successfully created demo user: {username}")

        # Verify the user can authenticate
        from django.contrib.auth import authenticate
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None:
            self.stdout.write("✅ Demo user authentication verified")
        else:
            self.stdout.write("❌ Demo user authentication failed")
            # Try to fix it
            user.set_password(password)
            user.save()
            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                self.stdout.write("✅ Demo user authentication fixed")
            else:
                self.stdout.write("❌ Demo user authentication still failing")

        # Create sample categories if they don't exist
        categories_data = [
            'Work Projects',
            'Personal Tasks', 
            'Learning & Development',
            'Health & Fitness',
            'Home & Family'
        ]
        
        categories = []
        for cat_title in categories_data:
            category, created = Category.objects.get_or_create(
                title=cat_title,
                user=user,
                defaults={'title': cat_title}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {cat_title}')

        # Create sample tasks if user has no tasks
        if not Task.objects.filter(user=user).exists():
            now = timezone.now()
            sample_tasks = [
                {
                    'title': 'Complete Django Todo App Documentation',
                    'description': 'Finish writing comprehensive documentation for the todo application including API docs and user guide.',
                    'category': categories[0],  # Work Projects
                    'priority': Priority.HIGH,
                    'status': Status.PROGRESS,
                    'progress': 75,
                    'start_date': now - timedelta(days=3),
                    'due_date': now + timedelta(days=2),
                },
                {
                    'title': 'Review and Merge Pull Requests',
                    'description': 'Review pending pull requests from team members and merge approved changes.',
                    'category': categories[0],  # Work Projects
                    'priority': Priority.MIDDLE,
                    'status': Status.NOT_COMPLETED,
                    'progress': 0,
                    'start_date': now,
                    'due_date': now + timedelta(days=1),
                },
                {
                    'title': 'Plan Weekend Trip',
                    'description': 'Research destinations, book accommodation, and plan activities for the weekend getaway.',
                    'category': categories[1],  # Personal Tasks
                    'priority': Priority.LOW,
                    'status': Status.NOT_COMPLETED,
                    'progress': 20,
                    'start_date': now,
                    'due_date': now + timedelta(days=7),
                },
                {
                    'title': 'Learn React Hooks',
                    'description': 'Complete online course on React Hooks and build a sample project to practice.',
                    'category': categories[2],  # Learning & Development
                    'priority': Priority.MIDDLE,
                    'status': Status.PROGRESS,
                    'progress': 45,
                    'start_date': now - timedelta(days=7),
                    'due_date': now + timedelta(days=14),
                },
                {
                    'title': 'Morning Workout Routine',
                    'description': 'Establish a consistent morning workout routine with cardio and strength training.',
                    'category': categories[3],  # Health & Fitness
                    'priority': Priority.HIGH,
                    'status': Status.PROGRESS,
                    'progress': 60,
                    'start_date': now - timedelta(days=14),
                    'due_date': now + timedelta(days=30),
                },
                {
                    'title': 'Organize Home Office',
                    'description': 'Declutter and reorganize the home office space for better productivity.',
                    'category': categories[4],  # Home & Family
                    'priority': Priority.LOW,
                    'status': Status.COMPLETED,
                    'progress': 100,
                    'start_date': now - timedelta(days=10),
                    'due_date': now - timedelta(days=2),
                },
                {
                    'title': 'Update Resume and LinkedIn',
                    'description': 'Update professional profiles with recent projects and achievements.',
                    'category': categories[0],  # Work Projects
                    'priority': Priority.MIDDLE,
                    'status': Status.NOT_COMPLETED,
                    'progress': 10,
                    'start_date': now + timedelta(days=1),
                    'due_date': now + timedelta(days=5),
                },
                {
                    'title': 'Read "Clean Code" Book',
                    'description': 'Read and take notes on Robert Martin\'s Clean Code principles.',
                    'category': categories[2],  # Learning & Development
                    'priority': Priority.LOW,
                    'status': Status.PROGRESS,
                    'progress': 30,
                    'start_date': now - timedelta(days=5),
                    'due_date': now + timedelta(days=21),
                },
            ]

            for task_data in sample_tasks:
                task = Task.objects.create(
                    user=user,
                    **task_data
                )
                self.stdout.write(f'Created task: {task.title}')

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {len(sample_tasks)} sample tasks for demo user'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Demo user already has tasks, skipping sample data creation'
                )
            )

        # Display summary
        task_count = Task.objects.filter(user=user).count()
        category_count = Category.objects.filter(user=user).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n--- Demo User Setup Complete ---\n'
                f'Username: {username}\n'
                f'Password: {password}\n'
                f'Email: {email}\n'
                f'Categories: {category_count}\n'
                f'Tasks: {task_count}\n'
                f'Demo URL: {os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8000")}'
            )
        )