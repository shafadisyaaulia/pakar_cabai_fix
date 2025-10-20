# Tugas Abdul: Implementasi formula perhitungan Certainty Factor (CF)

def combine_cf(cf1: float, cf2: float) -> float:
    """
    Formula penggabungan Certainty Factor (CF) untuk multiple evidence/rules
    yang mengarah pada kesimpulan yang sama.
    """
    if not (-1.0 <= cf1 <= 1.0 and -1.0 <= cf2 <= 1.0):
        raise ValueError("CF value must be between -1.0 and 1.0")

    if cf1 >= 0 and cf2 >= 0:
        # Kedua CF positif
        return cf1 + cf2 * (1 - cf1)
    elif cf1 <= 0 and cf2 <= 0:
        # Kedua CF negatif
        return cf1 + cf2 * (1 + cf1)
    else:
        # Satu positif, satu negatif
        # Formula: (CF1 + CF2) / (1 - min(|CF1|, |CF2|))
        return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))

def calculate_rule_cf(user_cf: float, rule_cf_pakar: float) -> float:
    """
    Menghitung Certainty Factor hipotesis (CF[H, E]).
    CF[H, E] = CF[E] * CF[H, e]
    user_cf (CF[E]): CF user terhadap gejala (disini diasumsikan 1.0 jika dipilih)
    rule_cf_pakar (CF[H, e]): CF pakar dalam rule
    """
    if not (-1.0 <= user_cf <= 1.0 and 0 <= rule_cf_pakar <= 1.0):
        raise ValueError("CF values are out of range.")
        
    return user_cf * rule_cf_pakar
