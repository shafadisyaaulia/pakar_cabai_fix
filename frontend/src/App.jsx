import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// URL API Python Flask
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Simple SVG Icons
const CheckIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const SearchIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <circle cx="11" cy="11" r="8"></circle>
    <path d="m21 21-4.35-4.35"></path>
  </svg>
);

const SparklesIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M12 3v18m9-9H3m15.66-6L5.34 18M18 18l-6.34-6.34M6 6l6.34 6.34"></path>
  </svg>
);

const LeafIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path>
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path>
  </svg>
);

const AlertIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>
);

const BeakerIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M4.5 3h15M6 3v16a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V3m-7 4v10m-4-5h8"></path>
  </svg>
);

// Symptom Images Mapping
const symptomImages = {
  'batang_cabai_rapuh_atau_pecah': 'https://images.unsplash.com/photo-1592837862203-8c2eadc5b31c?w=400&auto=format&fit=crop',
  'buah_bentuk_aneh': 'https://images.unsplash.com/photo-1583790337578-94c6e980934d?w=400&auto=format&fit=crop',
  'buah_berkembang_buruk': 'https://images.unsplash.com/photo-1557800636-894a64c1696f?w=400&auto=format&fit=crop',
  'buah_cabai_busuk_ujung_atau_pecah': 'https://images.unsplash.com/photo-1583790337578-94c6e980934d?w=400&auto=format&fit=crop',
  'daun_menguning_dari_bawah': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&auto=format&fit=crop',
  'daun_muda_distorsi': 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400&auto=format&fit=crop',
  'daun_muda_keriting_distorsi': 'https://images.unsplash.com/photo-1509587584298-0f3b3a3a1797?w=400&auto=format&fit=crop',
  'daun_muda_normal': 'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400&auto=format&fit=crop',
  'daun_tua_berwarna_ungu_gelap': 'https://images.unsplash.com/photo-1509587584298-0f3b3a3a1797?w=400&auto=format&fit=crop',
  'gagal_berbunga': 'https://images.unsplash.com/photo-1592837862203-8c2eadc5b31c?w=400&auto=format&fit=crop',
  'kuning_diantara_tulang_daun_tua': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&auto=format&fit=crop',
  'pertumbuhan_terhambat': 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400&auto=format&fit=crop',
  'tepi_daun_hangus_kecoklatan': 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400&auto=format&fit=crop',
  'titik_tumbuh_mati': 'https://images.unsplash.com/photo-1557800636-894a64c1696f?w=400&auto=format&fit=crop',
  'urat_daun_tetap_hijau': 'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400&auto=format&fit=crop',
};

// Format diagnosis name
const formatDiagnosisName = (name) => {
  if (!name) return "N/A";
  const parts = name.split('_');
  if (parts.length > 2) {
    return `${parts[0]} ${parts[1]} (${parts[2]})`;
  }
  return name.replace(/_/g, ' ');
};

const App = () => {
  const [fase, setFase] = useState('fase_vegetatif');
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState({ connected: false, message: 'Connecting...' });
  const [showExplanation, setShowExplanation] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch symptoms
  const fetchSymptoms = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/symptoms`);
      if (!response.ok) throw new Error("Failed to fetch symptoms");
      const data = await response.json();
      setSymptoms(data.symptoms);
      setApiStatus({ connected: true, message: 'Connected' });
    } catch (error) {
      console.error("Fetch Symptoms Error:", error);
      setSymptoms([]);
      setApiStatus({ connected: false, message: 'Disconnected' });
    }
  }, []);

  useEffect(() => {
    fetchSymptoms();
  }, [fetchSymptoms]);

  const handleSymptomChange = (symptom) => {
    setSelectedSymptoms(prev => 
      prev.includes(symptom) 
        ? prev.filter(s => s !== symptom) 
        : [...prev, symptom]
    );
  };

  const handleDiagnose = async () => {
    if (selectedSymptoms.length === 0) {
      alert("Pilih minimal satu gejala visual.");
      return;
    }

    setLoading(true);
    setDiagnosisResult(null);
    setShowExplanation(false);

    const payload = {
      fase: fase,
      symptoms: selectedSymptoms,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      const data = await response.json();
      
      if(data.success) {
        setDiagnosisResult(data.result);
      } else {
        alert('Error: ' + data.message);
      }
    } catch (error) {
      console.error('Fetch Diagnosis Error:', error);
      alert('Gagal menjalankan diagnosis.');
    } finally {
      setLoading(false);
    }
  };

  const filteredSymptoms = symptoms.filter(sym => 
    sym.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50">
      {/* Hero Header */}
      <header className="relative overflow-hidden bg-gradient-to-r from-emerald-600 to-teal-600 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="1"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          }} />
        </div>
        <div className="relative max-w-7xl mx-auto px-6 py-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="w-16 h-16 rounded-3xl bg-white/20 backdrop-blur-sm flex items-center justify-center text-4xl border-2 border-white/30">
                🌶️
              </div>
            </div>
            <h1 className="text-5xl font-bold mb-4 tracking-tight">ChiliCare Expert System</h1>
            <p className="text-xl text-emerald-50 mb-6 max-w-2xl mx-auto">
              Sistem diagnosis pintar untuk kesehatan tanaman cabai Anda
            </p>
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
              apiStatus.connected 
                ? 'bg-white/20 text-white border border-white/30' 
                : 'bg-red-500/20 text-red-100 border border-red-300/30'
            }`}>
              <div className={`w-2 h-2 rounded-full ${apiStatus.connected ? 'bg-white' : 'bg-red-300'} animate-pulse`} />
              <span className="text-sm font-medium">{apiStatus.message}</span>
            </div>
          </motion.div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Phase Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-100 flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-emerald-600" />
            </div>
            Pilih Fase Pertumbuhan
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { value: 'fase_vegetatif', label: 'Fase Vegetatif', desc: 'Pembentukan daun & akar', icon: '🌱', color: 'emerald' },
              { value: 'fase_generatif', label: 'Fase Generatif', desc: 'Pembungaan & pembuahan', icon: '🌸', color: 'violet' }
            ].map(phase => (
              <motion.button
                key={phase.value}
                whileHover={{ scale: 1.02, y: -4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setFase(phase.value)}
                className={`relative p-8 rounded-3xl transition-all duration-300 ${
                  fase === phase.value
                    ? `bg-gradient-to-br from-${phase.color}-500 to-${phase.color}-600 text-white shadow-2xl shadow-${phase.color}-500/30`
                    : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-gray-300 shadow-lg'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-5xl">{phase.icon}</div>
                  <div className={`w-8 h-8 rounded-xl border-2 flex items-center justify-center ${
                    fase === phase.value 
                      ? 'border-white bg-white/20'
                      : 'border-gray-300'
                  }`}>
                    {fase === phase.value && <CheckIcon className="w-5 h-5 text-white" />}
                  </div>
                </div>
                <h3 className="text-2xl font-bold mb-2">{phase.label}</h3>
                <p className={`text-sm ${fase === phase.value ? 'text-white/80' : 'text-gray-500'}`}>
                  {phase.desc}
                </p>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Symptoms Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-teal-100 flex items-center justify-center">
                <LeafIcon className="w-5 h-5 text-teal-600" />
              </div>
              Pilih Gejala Visual
            </h2>
            {selectedSymptoms.length > 0 && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="px-4 py-2 rounded-full bg-emerald-100 text-emerald-700 font-semibold text-sm"
              >
                {selectedSymptoms.length} gejala dipilih
              </motion.div>
            )}
          </div>

          {/* Search Bar */}
          <div className="relative mb-8">
            <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Cari gejala..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-4 rounded-2xl border-2 border-gray-200 focus:border-emerald-500 focus:outline-none transition-colors text-gray-700 bg-white shadow-sm"
            />
          </div>

          {/* Symptoms Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredSymptoms.length > 0 ? filteredSymptoms.map(sym => (
              <motion.div
                key={sym}
                whileHover={{ y: -8 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleSymptomChange(sym)}
                className={`relative cursor-pointer rounded-3xl overflow-hidden transition-all duration-300 ${
                  selectedSymptoms.includes(sym)
                    ? 'ring-4 ring-emerald-500 shadow-2xl shadow-emerald-500/30'
                    : 'ring-2 ring-gray-200 hover:ring-gray-300 shadow-lg'
                }`}
              >
                <div className="aspect-[4/3] relative overflow-hidden bg-gradient-to-br from-emerald-100 to-teal-100">
                  <img
                    src={symptomImages[sym] || 'https://images.unsplash.com/photo-1592837862203-8c2eadc5b31c?w=400&auto=format&fit=crop'}
                    alt={sym}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'https://images.unsplash.com/photo-1592837862203-8c2eadc5b31c?w=400&auto=format&fit=crop';
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
                </div>
                <div className="absolute top-3 right-3">
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center transition-all ${
                    selectedSymptoms.includes(sym)
                      ? 'bg-emerald-500 scale-110'
                      : 'bg-white/80 backdrop-blur-sm'
                  }`}>
                    {selectedSymptoms.includes(sym) && <CheckIcon className="w-5 h-5 text-white" />}
                  </div>
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
                  <p className="text-white font-semibold text-sm capitalize leading-tight">
                    {sym.replace(/_/g, ' ')}
                  </p>
                </div>
              </motion.div>
            )) : (
              <div className="col-span-full text-center py-20">
                <AlertIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <p className="text-gray-500 text-lg">Tidak ada gejala ditemukan</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Diagnose Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex justify-center mb-12"
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleDiagnose}
            disabled={loading || selectedSymptoms.length === 0 || !apiStatus.connected}
            className="px-12 py-6 rounded-3xl font-bold text-lg text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-2xl shadow-emerald-500/30 flex items-center gap-4"
          >
            {loading ? (
              <>
                <div className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Menganalisis Gejala...</span>
              </>
            ) : (
              <>
                <BeakerIcon className="w-6 h-6" />
                <span>Mulai Diagnosis</span>
              </>
            )}
          </motion.button>
        </motion.div>

        {/* Results Section */}
        <AnimatePresence mode="wait">
          {diagnosisResult && (
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -40 }}
              className="bg-white rounded-3xl shadow-2xl p-8 md:p-12 border-2 border-gray-100"
            >
              {/* Result Header */}
              <div className="text-center mb-10">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold mb-6 shadow-lg shadow-emerald-500/30"
                >
                  <CheckIcon className="w-5 h-5" />
                  Diagnosis Selesai
                </motion.div>
                <h2 className="text-4xl font-bold text-gray-800 mb-4">
                  {formatDiagnosisName(diagnosisResult.diagnosis)}
                </h2>
                <div className="flex items-center justify-center gap-4">
                  <span className="text-gray-500">Tingkat Kepastian:</span>
                  <div className="flex items-center gap-3">
                    <div className="w-48 h-3 bg-gray-200 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${diagnosisResult.certainty_factor * 100}%` }}
                        transition={{ duration: 1, ease: "easeOut" }}
                        className={`h-full rounded-full ${
                          diagnosisResult.certainty_factor >= 0.8 
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-600' 
                            : 'bg-gradient-to-r from-yellow-500 to-orange-600'
                        }`}
                      />
                    </div>
                    <span className="text-2xl font-bold text-emerald-600">
                      {Math.round(diagnosisResult.certainty_factor * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Recommendation Card */}
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-8 mb-8 border-2 border-emerald-100">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                    <LeafIcon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-800">Rekomendasi Pemupukan</h3>
                </div>
                <div className="bg-white rounded-2xl p-6 shadow-sm">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-line text-lg">
                    {diagnosisResult.recommendation}
                  </p>
                </div>
              </div>

              {/* Explanation Toggle */}
              <div className="text-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowExplanation(!showExplanation)}
                  className="px-8 py-4 rounded-2xl font-semibold bg-gradient-to-r from-violet-500 to-purple-600 text-white hover:from-violet-600 hover:to-purple-700 transition-all shadow-lg shadow-violet-500/30"
                >
                  {showExplanation ? 'Sembunyikan' : 'Tampilkan'} Alur Penalaran
                </motion.button>
              </div>

              {/* Explanation */}
              <AnimatePresence>
                {showExplanation && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden mt-8"
                  >
                    <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-3xl p-8 border-2 border-violet-100">
                      <h4 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-3">
                        <BeakerIcon className="w-6 h-6 text-violet-600" />
                        Proses Penalaran Sistem
                      </h4>
                      <div className="bg-white rounded-2xl p-6 shadow-sm">
                        <pre className="text-sm text-gray-700 font-mono leading-relaxed overflow-x-auto">
                          {diagnosisResult.explanation}
                        </pre>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default App;