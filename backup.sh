#!/bin/bash
# Бэкап базы SkrepNet Bot
BACKUP_DIR="/root/skrepnet-bot/backups"
DB_FILE="/root/skrepnet-bot/skrepnet.db"
DATE=$(date +%Y-%m-%d_%H-%M)

# Создаём копию
cp "$DB_FILE" "$BACKUP_DIR/skrepnet-$DATE.db"

# Удаляем бэкапы старше 30 дней
find "$BACKUP_DIR" -name "skrepnet-*.db" -mtime +30 -delete

echo "$(date '+%Y-%m-%d %H:%M:%S') Backup created: skrepnet-$DATE.db"
