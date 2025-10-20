# Tugas Davina: Modul penjelasan HOW (alur) dan WHY (mengapa ditanya)

def generate_how_explanation(conclusion, final_cf, reasoning_path, rules_data):
    """
    Menjelaskan bagaimana sistem sampai pada kesimpulan (HOW).
    """
    if not reasoning_path:
        return "Sistem belum menemukan alur penalaran yang kuat untuk diagnosis ini."

    explanation = (
        f"Sistem menyimpulkan adanya '{conclusion.replace('_', ' ')}' dengan Faktor Kepastian (CF) sebesar {final_cf:.3f} "
        f"berdasarkan rule-rule yang memiliki kesesuaian tertinggi dari data input Anda.\n\n"
        f"Rule-rule yang digunakan untuk mencapai diagnosis ini:\n"
    )
    
    for i, rule_id in enumerate(reasoning_path):
        rule = rules_data.get(rule_id, {})
        if rule:
            if_str = " DAN ".join(cond.replace('_', ' ') for cond in rule.get('IF', []))
            cf_rule = rule.get('CF', 0.0)
            
            explanation += (
                f"• {rule_id} (CF Pakar: {cf_rule:.2f}):\n"
                f"  JIKA: {if_str.upper()}\n"
                f"  MAKA: {conclusion.replace('_', ' ')}\n"
            )
        else:
            explanation += f"• {rule_id} tidak ditemukan dalam basis pengetahuan.\n"

    explanation += "\nRule-rule ini saling mendukung, menyebabkan CF diagnosis Anda menjadi tinggi."
    
    return explanation

def generate_why_explanation(symptom):
    """
    Menjelaskan mengapa gejala ini ditanyakan (WHY).
    Fungsi ini biasanya dipanggil jika sistem meminta gejala tambahan (tidak diimplementasikan di sini).
    Namun, Davina dapat menggunakannya untuk memberikan tooltip/hover di UI.
    """
    symptom_map = {
        'fase_vegetatif': "Memengaruhi kebutuhan N (pertumbuhan daun) dan P (akar).",
        'fase_generatif': "Memengaruhi kebutuhan K (buah), Ca (kualitas buah), dan B (bunga/buah).",
        'daun_menguning_dari_bawah': "Gejala klasik kekurangan Nitrogen (N) karena N mudah dimobilisasi ke daun muda.",
        'pertumbuhan_terhambat_tanaman_kerdil': "Gejala umum yang dapat disebabkan oleh kekurangan P, Mg, atau B.",
        'tepi_daun_hangus_kecoklatan': "Gejala khas kekurangan Kalium (K), sering disebut 'scorching'.",
        'buah_cabai_busuk_ujung_atau_pecah': "Gejala utama kekurangan Kalsium (Ca), dikenal sebagai 'Blossom End Rot' (BER).",
        'daun_muda_keriting_distorsi': "Gejala khas kekurangan unsur hara yang imobil (tidak bergerak) seperti Kalsium (Ca) atau Boron (B).",
        'daun_tua_berwarna_ungu_gelap': "Gejala klasik kekurangan Fosfor (P), terutama saat suhu dingin.",
        'kuning_diantara_tulang_daun_tua': "Gejala khas kekurangan Magnesium (Mg) atau Kadang Kalium (K), disebut klorosis interveinal."
    }
    
    why_explanation = symptom_map.get(symptom, f"Gejala '{symptom.replace('_', ' ')}' adalah indikator visual yang dicari untuk membedakan antar defisiensi unsur hara.")
    return f"Gejala ini ditanyakan karena: {why_explanation}"
