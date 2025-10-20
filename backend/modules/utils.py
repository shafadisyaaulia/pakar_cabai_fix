import json
import csv
from datetime import datetime
import os

def load_from_json(filename):
    """Memuat data dari file JSON."""
    try:
        # Membuat path absolut
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', filename)
        if not os.path.exists(full_path):
            print(f"File {full_path} tidak ditemukan. Mengembalikan dict kosong.")
            return {}
        with open(full_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error saat memuat JSON dari {filename}: {e}")
        return {}

def save_to_json(data, filename):
    """Menyimpan data (misal rules) ke file JSON."""
    try:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', filename)
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data berhasil disimpan ke {filename}")
    except Exception as e:
        print(f"Error saat menyimpan JSON ke {filename}: {e}")

def log_consultation(data, filename='consultation_log.csv'):
    """Mencatat hasil konsultasi ke file CSV. (Tugas Thahira)"""
    # Menyimpan file log di root backend/
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', filename)

    log_data = data.copy()
    log_data['timestamp'] = datetime.now().isoformat()
    
    # Header untuk CSV
    fieldnames = ['timestamp', 'fase', 'symptoms_input', 'diagnosis', 'certainty_factor', 'recommendation', 'reasoning_path']
    file_exists = os.path.isfile(log_file_path)
    
    try:
        with open(log_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            # Konversi list menjadi string
            if isinstance(log_data.get('symptoms_input'), list):
                log_data['symptoms_input'] = "; ".join(log_data['symptoms_input'])
            if isinstance(log_data.get('reasoning_path'), list):
                log_data['reasoning_path'] = "; ".join(log_data['reasoning_path'])

            writer.writerow(log_data)
        
    except Exception as e:
        print(f"Error saat mencatat log: {e}")
        
