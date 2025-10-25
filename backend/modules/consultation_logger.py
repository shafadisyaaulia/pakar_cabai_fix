import csv
from datetime import datetime
import json

class ConsultationLogger:
    def __init__(self, filename):
        self.filename = filename
    
    def log_consultation(self, data: dict):
        headers = [
            'consultation_id', 'timestamp', 'symptoms', 'conclusions'
        ]
        try:
            # Cek jika file belum ada dan buat header
            try:
                with open(self.filename, 'r', newline='', encoding='utf-8') as f:
                    pass
            except FileNotFoundError:
                with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
            
            # Serialisasi conclusions dengan penanganan error
            try:
                conclusions_json = json.dumps(data.get('conclusions', []), default=str)
            except (TypeError, ValueError) as e:
                conclusions_json = '[]'  # fallback
                print(f"Warning: failed to serialize conclusions: {e}")
            
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                row = {
                    'consultation_id': data.get('consultation_id'),
                    'timestamp': data.get('timestamp'),
                    'symptoms': ','.join(data.get('facts', [])),
                    'conclusions': conclusions_json
                }
                writer.writerow(row)
        except Exception as e:
            print(f"Failed to log consultation: {e}")
    
    def load_history(self):
        import pandas as pd
        try:
            return pd.read_csv(self.filename)
        except FileNotFoundError:
            return pd.DataFrame()
    

    def error(self, message, exc_info=False):
        """Menangani log error agar kompatibel dengan app.logger.error()."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[ERROR] {timestamp} - {message}"

        if exc_info:
            import traceback
            log_message += "\n" + traceback.format_exc()

        print(log_message)  # tampilkan juga di console untuk debugging

        # Simpan error ke file log CSV (opsional)
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ERROR', timestamp, log_message])
        except Exception as e:
            print(f"Gagal menulis log error: {e}")

    def info(self, message):
        """Tambahan agar bisa juga memanggil app.logger.info()"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO] {timestamp} - {message}")
