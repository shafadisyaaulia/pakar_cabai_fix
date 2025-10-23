import React, { useState } from 'react';
import { Leaf, Sprout, FlaskConical, BookOpen, BarChart3, Info, ChevronRight, CheckCircle2, AlertCircle } from 'lucide-react';

const ExpertSystemUI = () => {
  const [activeMenu, setActiveMenu] = useState('home');
  const [selectedSymptoms, setSelectedSymptoms] = useState({});
  const [selectedPhase, setSelectedPhase] = useState({ vegetatif: false, generatif: false });
  const [diagnosisResult, setDiagnosisResult] = useState(null);

  // Symptom categories
  const symptomCategories = {
    'Gejala Daun': [
      'daun_kuning_merata',
      'daun_muda_kuning',
      'daun_tua_kuning',
      'tepi_daun_kuning_kecoklatan',
      'daun_menggulung',
      'tulang_daun_ungu',
      'tulang_daun_hijau',
      'daun_pucat_kekuningan'
    ],
    'Gejala Pertumbuhan': [
      'pertumbuhan_lambat',
      'pertumbuhan_kerdil',
      'ruas_batang_pendek',
      'pertumbuhan_abnormal'
    ],
    'Gejala Bunga & Buah': [
      'bunga_rontok',
      'pembentukan_buah_sedikit',
      'buah_kecil',
      'ujung_buah_busuk',
      'bercak_hitam_ujung_buah',
      'warna_buah_pucat',
      'pematangan_tidak_merata'
    ],
    'Kondisi Lain': [
      'kualitas_rendah',
      'produksi_menurun',
      'tanah_pH_rendah'
    ]
  };

  const formatSymptomName = (symptom) => {
    return symptom.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const handleSymptomChange = (symptom) => {
    setSelectedSymptoms(prev => {
      const newSymptoms = { ...prev };
      if (newSymptoms[symptom]) {
        delete newSymptoms[symptom];
      } else {
        newSymptoms[symptom] = 0.8;
      }
      return newSymptoms;
    });
  };

  const handleCFChange = (symptom, value) => {
    setSelectedSymptoms(prev => ({
      ...prev,
      [symptom]: parseFloat(value)
    }));
  };

  const runDiagnosis = () => {
    // Simulate diagnosis
    const mockResult = {
      conclusions: [
        {
          diagnosis: 'Kekurangan Nitrogen (N)',
          cf: 0.85,
          cf_interpretation: 'Sangat Meyakinkan',
          recommendation: {
            pupuk: 'Urea atau ZA',
            dosis: '150-200 kg/ha atau 15-20 gram/tanaman',
            metode: 'Aplikasi bertahap setiap 2 minggu'
          },
          explanation: 'Nitrogen sangat penting untuk pertumbuhan vegetatif. Daun kuning merata dan pertumbuhan lambat adalah indikator kuat kekurangan N.'
        }
      ]
    };
    setDiagnosisResult(mockResult);
  };

  const resetConsultation = () => {
    setSelectedSymptoms({});
    setSelectedPhase({ vegetatif: false, generatif: false });
    setDiagnosisResult(null);
  };

  // Menu Components
  const HomePage = () => (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative h-96 rounded-2xl overflow-hidden shadow-xl">
        <img 
          src="https://images.unsplash.com/photo-1583419319058-d0b57fbb1364?q=80&w=2000" 
          alt="Chili Plants"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent flex items-end">
          <div className="p-8 text-white">
            <h1 className="text-4xl font-bold mb-3">🌶️ Sistem Pakar Pemupukan Cabai</h1>
            <p className="text-lg text-gray-200">Expert System for Chili Fertilization Recommendation</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Rules', value: '12', icon: BookOpen, color: 'bg-blue-500' },
          { label: 'Diagnosis Unik', value: '10', icon: FlaskConical, color: 'bg-green-500' },
          { label: 'Avg CF', value: '0.86', icon: BarChart3, color: 'bg-purple-500' },
          { label: 'Total Nutrisi', value: '8', icon: Sprout, color: 'bg-orange-500' }
        ].map((stat, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
              <stat.icon className="w-6 h-6 text-white" />
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">{stat.value}</div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* About Section */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 shadow-md">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Tentang Sistem</h2>
        <p className="text-gray-700 leading-relaxed mb-4">
          Sistem ini menggunakan aturan berbasis IF-THEN dan mekanisme penalaran Forward Chaining 
          dengan Certainty Factor (CF) untuk merekomendasikan jenis dan dosis pupuk yang tepat 
          untuk tanaman cabai Anda.
        </p>
        <button 
          onClick={() => setActiveMenu('consultation')}
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors"
        >
          Mulai Konsultasi <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );

  const ConsultationPage = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">🔍 Konsultasi Pemupukan</h2>

        {/* Phase Selection */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Step 1: Pilih Fase Pertumbuhan</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="relative cursor-pointer">
              <input
                type="checkbox"
                checked={selectedPhase.vegetatif}
                onChange={(e) => setSelectedPhase(prev => ({ ...prev, vegetatif: e.target.checked }))}
                className="peer sr-only"
              />
              <div className="bg-white border-2 peer-checked:border-green-500 peer-checked:bg-green-50 rounded-xl p-6 transition-all hover:shadow-md">
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full border-2 peer-checked:bg-green-500 peer-checked:border-green-500 mt-1 flex items-center justify-center">
                    <CheckCircle2 className="w-4 h-4 text-white opacity-0 peer-checked:opacity-100" />
                  </div>
                  <div>
                    <div className="font-semibold text-gray-800">Fase Vegetatif</div>
                    <div className="text-sm text-gray-600">0-60 HST (Hari Setelah Tanam)</div>
                  </div>
                </div>
              </div>
            </label>
            
            <label className="relative cursor-pointer">
              <input
                type="checkbox"
                checked={selectedPhase.generatif}
                onChange={(e) => setSelectedPhase(prev => ({ ...prev, generatif: e.target.checked }))}
                className="peer sr-only"
              />
              <div className="bg-white border-2 peer-checked:border-green-500 peer-checked:bg-green-50 rounded-xl p-6 transition-all hover:shadow-md">
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full border-2 peer-checked:bg-green-500 peer-checked:border-green-500 mt-1 flex items-center justify-center">
                    <CheckCircle2 className="w-4 h-4 text-white opacity-0 peer-checked:opacity-100" />
                  </div>
                  <div>
                    <div className="font-semibold text-gray-800">Fase Generatif</div>
                    <div className="text-sm text-gray-600">&gt;60 HST</div>
                  </div>
                </div>
              </div>
            </label>
          </div>
        </div>

        {/* Symptoms Selection */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Step 2: Pilih Gejala yang Terlihat</h3>
          <div className="space-y-4">
            {Object.entries(symptomCategories).map(([category, symptoms]) => (
              <details key={category} className="group bg-gray-50 rounded-xl overflow-hidden">
                <summary className="cursor-pointer p-4 font-medium text-gray-800 hover:bg-gray-100 transition-colors list-none flex items-center justify-between">
                  <span>📋 {category}</span>
                  <ChevronRight className="w-5 h-5 group-open:rotate-90 transition-transform" />
                </summary>
                <div className="p-4 space-y-3 bg-white">
                  {symptoms.map(symptom => (
                    <div key={symptom} className="flex items-center gap-3">
                      <label className="flex-1 flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={!!selectedSymptoms[symptom]}
                          onChange={() => handleSymptomChange(symptom)}
                          className="w-5 h-5 rounded border-gray-300 text-green-600 focus:ring-green-500"
                        />
                        <span className="text-gray-700">{formatSymptomName(symptom)}</span>
                      </label>
                      {selectedSymptoms[symptom] !== undefined && (
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={selectedSymptoms[symptom]}
                          onChange={(e) => handleCFChange(symptom, e.target.value)}
                          className="w-24 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                        />
                      )}
                      {selectedSymptoms[symptom] !== undefined && (
                        <span className="text-sm text-gray-600 w-12">{(selectedSymptoms[symptom] * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  ))}
                </div>
              </details>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={runDiagnosis}
            disabled={Object.keys(selectedSymptoms).length === 0}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white py-3 rounded-xl font-medium transition-colors"
          >
            🧠 Diagnosis
          </button>
          <button
            onClick={resetConsultation}
            className="px-6 bg-gray-200 hover:bg-gray-300 text-gray-800 py-3 rounded-xl font-medium transition-colors"
          >
            🔄 Reset
          </button>
        </div>
      </div>

      {/* Results */}
      {diagnosisResult && (
        <div className="bg-white rounded-2xl shadow-lg p-6 space-y-6">
          <div className="flex items-center gap-3 text-green-600">
            <CheckCircle2 className="w-8 h-8" />
            <h3 className="text-2xl font-bold">Diagnosis Selesai!</h3>
          </div>

          {diagnosisResult.conclusions.map((conclusion, idx) => (
            <div key={idx} className="border-l-4 border-green-500 bg-green-50 rounded-r-xl p-6">
              <h4 className="text-xl font-bold text-gray-800 mb-4">{idx + 1}. {conclusion.diagnosis}</h4>
              
              <div className="mb-4">
                <div className="text-sm text-gray-600 mb-1">Tingkat Kepercayaan</div>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div 
                      className="bg-green-500 h-full rounded-full transition-all"
                      style={{ width: `${conclusion.cf * 100}%` }}
                    />
                  </div>
                  <span className="font-bold text-green-600">{(conclusion.cf * 100).toFixed(1)}%</span>
                  <span className="text-sm text-gray-600">({conclusion.cf_interpretation})</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-sm text-gray-600 mb-1">Pupuk</div>
                  <div className="font-semibold text-gray-800">{conclusion.recommendation.pupuk}</div>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-sm text-gray-600 mb-1">Dosis</div>
                  <div className="font-semibold text-gray-800">{conclusion.recommendation.dosis}</div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm text-gray-600 mb-1">Metode Aplikasi</div>
                <div className="font-semibold text-gray-800">{conclusion.recommendation.metode}</div>
              </div>

              <details className="mt-4">
                <summary className="cursor-pointer text-green-700 font-medium hover:text-green-800 list-none flex items-center gap-2">
                  <span>📖 Penjelasan</span>
                  <ChevronRight className="w-4 h-4" />
                </summary>
                <div className="mt-3 text-gray-700 leading-relaxed pl-6">
                  {conclusion.explanation}
                </div>
              </details>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const KnowledgeBasePage = () => (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">📚 Knowledge Base</h2>
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-6">
        <div className="flex items-start gap-3">
          <Info className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">Tentang Knowledge Base</h3>
            <p className="text-blue-800 text-sm leading-relaxed">
              Sistem ini menggunakan 12 rules yang telah divalidasi berdasarkan penelitian dari 
              Balai Penelitian Tanaman Sayuran (Balitsa) dan praktisi pertanian berpengalaman.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {[
          { id: 'R1', diagnosis: 'Kekurangan Nitrogen (N)', cf: 0.9, conditions: 3 },
          { id: 'R2', diagnosis: 'Kekurangan Fosfor (P)', cf: 0.85, conditions: 3 },
          { id: 'R3', diagnosis: 'Kekurangan Kalium (K)', cf: 0.88, conditions: 3 },
          { id: 'R8', diagnosis: 'Kekurangan Kalsium (Ca) - BER', cf: 0.92, conditions: 3 }
        ].map((rule) => (
          <div key={rule.id} className="border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="text-sm text-gray-600 mb-1">Rule {rule.id}</div>
                <div className="font-semibold text-gray-800 text-lg">{rule.diagnosis}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">CF</div>
                <div className="text-xl font-bold text-green-600">{(rule.cf * 100).toFixed(0)}%</div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="bg-gray-100 px-3 py-1 rounded-full">{rule.conditions} kondisi</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const AboutPage = () => (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">ℹ️ Tentang Sistem</h2>
      
      <div className="prose max-w-none">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 mb-6">
          <h3 className="text-xl font-bold text-gray-800 mb-3">Sistem Pakar Pemupukan Cabai</h3>
          <div className="space-y-2 text-gray-700">
            <p><strong>Versi:</strong> 1.0</p>
            <p><strong>Metode:</strong> Rule-based system (IF-THEN), Forward Chaining + Certainty Factor</p>
            <p><strong>Sumber:</strong> Balai Penelitian Tanaman Sayuran (Balitsa)</p>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Fitur Utama:</h3>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span>Diagnosis defisiensi nutrisi berdasarkan gejala visual</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span>Rekomendasi pupuk, dosis, dan metode aplikasi yang spesifik</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span>Perhitungan tingkat kepercayaan (Certainty Factor)</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span>Penjelasan alur penalaran sistem (explainable AI)</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );

  // Navigation
  const menuItems = [
    { id: 'home', label: 'Beranda', icon: Leaf },
    { id: 'consultation', label: 'Konsultasi', icon: FlaskConical },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
    { id: 'about', label: 'Tentang', icon: Info }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Leaf className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="font-bold text-gray-800 text-lg">Sistem Pakar</div>
                <div className="text-xs text-gray-600">Pemupukan Cabai</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <aside className="lg:w-64 flex-shrink-0">
            <nav className="bg-white rounded-2xl shadow-md p-4 space-y-2 sticky top-24">
              {menuItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => setActiveMenu(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
                    activeMenu === item.id
                      ? 'bg-green-600 text-white shadow-md'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </button>
              ))}
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            {activeMenu === 'home' && <HomePage />}
            {activeMenu === 'consultation' && <ConsultationPage />}
            {activeMenu === 'knowledge' && <KnowledgeBasePage />}
            {activeMenu === 'about' && <AboutPage />}
          </main>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600 text-sm">
            © 2025 Sistem Pakar Pemupukan Cabai. Powered by Forward Chaining & Certainty Factor.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ExpertSystemUI;