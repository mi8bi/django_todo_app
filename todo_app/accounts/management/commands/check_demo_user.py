"""
Django management command to check if demo user exists and verify credentials
Place this file at: todo_app/accounts/management/commands/check_demo_user.py
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class Command(BaseCommand):
    help = 'Check demo user credentials and status'

    def handle(self, *args, **options):
        username = 'demo_user'
        password = 'demo123456'

        self.stdout.write("=== Demo User Check ===")

        # Check if user exists
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"✅ User exists: {username}")
            self.stdout.write(f"   - Email: {user.email}")
            self.stdout.write(f"   - Active: {user.is_active}")
            self.stdout.write(f"   - Staff: {user.is_staff}")
            self.stdout.write(f"   - Superuser: {user.is_superuser}")
            self.stdout.write(f"   - Date joined: {user.date_joined}")
            self.stdout.write(f"   - Last login: {user.last_login}")
            
            # Test authentication
            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                self.stdout.write(f"✅ Authentication successful")
            else:
                self.stdout.write(f"❌ Authentication failed")
                self.stdout.write("   - Password may be incorrect")
                
                # Reset password for demo user
                user.set_password(password)
                user.save()
                self.stdout.write("🔧 Password has been reset")
                
                # Test again
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    self.stdout.write(f"✅ Authentication successful after reset")
                else:
                    self.stdout.write(f"❌ Authentication still failing")
                    
        except User.DoesNotExist:
            self.stdout.write(f"❌ User does not exist: {username}")
            self.stdout.write("🔧 Creating demo user...")
            
            user = User.objects.create_user(
                username=username,
                email='demo@example.com',
                password=password,
                is_active=True
            )
            self.stdout.write(f"✅ Demo user created successfully")
            
        # Show all users for debugging
        self.stdout.write("\n=== All Users ===")
        users = User.objects.all()
        for user in users:
            self.stdout.write(f"- {user.username} (active: {user.is_active})")
            
        self.stdout.write(f"\nTotal users: {users.count()}")