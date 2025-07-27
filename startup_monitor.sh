#!/bin/bash

echo "🚀 Starting Django Todo App with monitoring..."
start_time=$(date +%s)

echo "📊 Step 1: Database migration..."
step1_start=$(date +%s)
python manage.py migrate --run-syncdb --verbosity 0
step1_end=$(date +%s)
echo "   ✅ Migration completed in $((step1_end - step1_start)) seconds"

echo "📊 Step 2: Demo user creation..."
step2_start=$(date +%s)
python manage.py create_demo_user --verbosity 0 --skip-sample-data
step2_end=$(date +%s)
echo "   ✅ Demo user created in $((step2_end - step2_start)) seconds"

echo "📊 Step 3: Starting Gunicorn..."
step3_start=$(date +%s)
echo "   🌟 Total startup preparation: $((step3_start - start_time)) seconds"

# Start Gunicorn with optimized settings
exec gunicorn todo_app.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 1 \
  --worker-class sync \
  --timeout 60 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --preload \
  --access-logfile - \
  --error-logfile - \
  --log-level warning