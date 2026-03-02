.PHONY: start stop restart pull deploy migrate shell test

start:
	@echo "🚀 Starting Docker containers..."
	docker compose up -d --build
	@echo "✅ Containers are running."

stop:
	@echo "🛑 Stopping Docker containers..."
	docker compose down
	@echo "✅ Containers stopped."

restart:
	@echo "🔄 Restarting Docker containers..."
	docker compose down
	docker compose up -d
	@echo "✅ Containers restarted."

pull:
	@echo "🔄 Pulling latest changes from git..."
	git pull

deploy: pull stop start
	@echo "✅ Deployment complete!"

migrate:
	@echo "📦 Running database migrations..."
	python manage.py migrate

shell:
	@echo "🐚 Opening Django shell..."
	python manage.py shell

test:
	@echo "🧪 Running tests..."
	python manage.py test
