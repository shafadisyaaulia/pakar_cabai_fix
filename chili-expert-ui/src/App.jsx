import React, { useState, useEffect } from 'react';
import { 
  Leaf, 
  Sprout, 
  FlaskConical, 
  BookOpen, 
  BarChart3, 
  Info, 
  ChevronRight, 
  CheckCircle2, 
  AlertCircle, 
  Loader2,
  Clock
} from 'lucide-react';
import { 
  fetchSymptoms, 
  diagnose, 
  fetchRules, 
  deleteRule, 
  updateRule, 
  exportPDF, 
  fetchHistory,
  fetchSummaryReport,
  fetchTopDiagnoses
} from './api/api.js';
import { toast, Toaster } from 'react-hot-toast';
import cabaiImg from './assets/cabai.avif';


const itemsPerPage = 5;

const ExpertSystemUI = () => {
  const [activeMenu, setActiveMenu] = useState('home');
  const [selectedSymptoms, setSelectedSymptoms] = useState({});
  const [selectedPhase, setSelectedPhase] = useState({ vegetatif: false, generatif: false });
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [symptomCategories, setSymptomCategories] = useState({});
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [openCategory, setOpenCategory] = useState(null);
  const [editingRule, setEditingRule] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);



  // Load symptoms and rules on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [symptomsData, rulesData] = await Promise.all([
          fetchSymptoms(),
          fetchRules()
        ]);
        setSymptomCategories(symptomsData);
        setRules(rulesData);
      } catch (err) {
        setError('Failed to load data from server');
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

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

   const runDiagnosis = async () => {
  // Ambil semua gejala yang dipilih
  const facts = Object.keys(selectedSymptoms);
  const user_cfs = { ...selectedSymptoms };

  // Tambahkan fakta fase pertumbuhan (biar dikirim ke backend)
  if (selectedPhase.vegetatif) {
    facts.push("fase_vegetatif");
    user_cfs["fase_vegetatif"] = 1.0;
  }
  if (selectedPhase.generatif) {
    facts.push("fase_generatif");
    user_cfs["fase_generatif"] = 1.0;
  }

  console.log("🔍 Data dikirim ke backend:", facts);

  try {
    setLoading(true);
    const response = await diagnose(facts, user_cfs);
    setDiagnosisResult(response);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};

  const resetConsultation = () => {
    setSelectedSymptoms({});
    setSelectedPhase({ vegetatif: false, generatif: false });
    setDiagnosisResult(null);
  };

  // Pagination handlers
  const paginatedRules = rules.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
  const totalPages = Math.ceil(rules.length / itemsPerPage);

  const handleDeleteRule = async (ruleId) => {
  try {
    await deleteRule(ruleId);
    setRules(prev => prev.filter(rule => rule.id !== ruleId));
    toast.success(`✅ Rule ${ruleId} berhasil dihapus`);
  } catch (err) {
    toast.error(`❌ Gagal menghapus rule ${ruleId}`);
    console.error(err);
  }
};


  const handleUpdateRule = async (ruleId, updatedData) => {
  try {
    await updateRule(ruleId, updatedData);
    toast.success(`✅ Rule ${ruleId} berhasil diperbarui!`);
    // Refresh daftar rules agar data terbaru muncul
    const refreshedRules = await fetchRules();
    setRules(refreshedRules);
  } catch (err) {
    console.error("Update rule gagal:", err);
    toast.error("❌ Gagal memperbarui rule.");
  }
};



  // Menu Components
  const HomePage = () => (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative h-96 rounded-2xl overflow-hidden shadow-xl">
      <img
        src={cabaiImg}
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
          { label: 'Total Rules', value: rules.length.toString(), icon: BookOpen, color: 'bg-blue-500' },
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

const ConsultationPage = () => {
  const [openCategory, setOpenCategory] = useState(null);
  const [selectedSymptoms, setSelectedSymptoms] = useState({});
  const [selectedPhase, setSelectedPhase] = useState({
    vegetatif: false,
    generatif: false,
  });
  const [symptomCategories, setSymptomCategories] = useState({});
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load symptoms dari backend
  useEffect(() => {
    const loadSymptoms = async () => {
      try {
        const data = await fetchSymptoms();
        setSymptomCategories(data);
      } catch (err) {
        console.error("Error loading symptoms:", err);
        setError("Gagal memuat data gejala");
      }
    };
    loadSymptoms();
  }, []);

  // Toggle symptom dengan CF default 0.8
  const handleSymptomToggle = (symptom) => {
    setSelectedSymptoms((prev) => {
      const updated = { ...prev };
      if (updated[symptom]) {
        delete updated[symptom];
      } else {
        updated[symptom] = 0.8; // CF default
      }
      return updated;
    });
  };

  // Update CF untuk symptom tertentu
  const handleCFChange = (symptom, cfValue) => {
    setSelectedSymptoms((prev) => ({
      ...prev,
      [symptom]: parseFloat(cfValue),
    }));
  };

  // Jalankan diagnosis
  const runDiagnosis = async () => {
    try {
      setLoading(true);
      setError(null);

      const selectedSymptomsArray = Object.keys(selectedSymptoms);

      if (selectedSymptomsArray.length === 0) {
        setError("Pilih minimal satu gejala!");
        return;
      }

      if (!selectedPhase.vegetatif && !selectedPhase.generatif) {
        setError("Pilih fase pertumbuhan!");
        return;
      }

      const fase = selectedPhase.vegetatif ? "fase_vegetatif" : "fase_generatif";

      // Kirim dengan CF user
      const result = await diagnose(selectedSymptomsArray, fase, selectedSymptoms);

      setDiagnosisResult(result);
    } catch (err) {
      console.error("Error during diagnosis:", err);
      setError("Gagal melakukan diagnosis. Silakan coba lagi.");
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const resetConsultation = () => {
    setSelectedSymptoms({});
    setSelectedPhase({ vegetatif: false, generatif: false });
    setDiagnosisResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <div className="min-h-screen w-full bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 py-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          🔍 Konsultasi Pemupukan
        </h2>

        {/* Step 1: Fase Pertumbuhan */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Step 1: Pilih Fase Pertumbuhan
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              {
                key: "vegetatif",
                label: "Fase Vegetatif",
                desc: "0-60 HST (Hari Setelah Tanam)",
              },
              {
                key: "generatif",
                label: "Fase Generatif",
                desc: ">60 HST",
              },
            ].map((phase) => (
              <label key={phase.key} className="relative cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedPhase[phase.key]}
                  onChange={(e) =>
                    setSelectedPhase((prev) => ({
                      ...prev,
                      [phase.key]: e.target.checked,
                    }))
                  }
                  className="peer sr-only"
                />
                <div className="bg-white border-2 peer-checked:border-green-500 peer-checked:bg-green-50 rounded-xl p-6 transition-all hover:shadow-md">
                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full border-2 border-gray-300 peer-checked:bg-green-500 peer-checked:border-green-500 mt-1 flex items-center justify-center">
                      {selectedPhase[phase.key] && (
                        <CheckCircle2 className="w-4 h-4 text-white" />
                      )}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">
                        {phase.label}
                      </div>
                      <div className="text-sm text-gray-600">{phase.desc}</div>
                    </div>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Step 2: Pilih Gejala dengan CF Slider */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Step 2: Pilih Gejala yang Terlihat
          </h3>
          <div className="space-y-4">
            {Object.entries(symptomCategories).map(([category, symptoms]) => (
              <div
                key={category}
                className="border rounded-lg bg-white shadow-md overflow-hidden"
              >
                {/* Header kategori */}
                <div
                  onClick={() =>
                    setOpenCategory(openCategory === category ? null : category)
                  }
                  className="cursor-pointer select-none text-lg font-semibold bg-green-100 p-3 rounded-t-lg hover:bg-green-200 transition-colors flex justify-between items-center"
                >
                  <span>{category}</span>
                  <span className="text-gray-500">
                    {openCategory === category ? "▲" : "▼"}
                  </span>
                </div>

                {/* Isi gejala */}
                {openCategory === category && (
                  <div className="p-4 space-y-4">
                    {symptoms.map((symptom) => (
                      <div key={symptom} className="flex flex-col gap-2">
                        {/* Checkbox dan Label */}
                        <label className="flex items-center gap-3 p-3 rounded-lg hover:bg-green-50 transition-colors cursor-pointer">
                          <input
                            type="checkbox"
                            checked={!!selectedSymptoms[symptom]}
                            onChange={() => handleSymptomToggle(symptom)}
                            className="w-5 h-5 text-green-600 rounded focus:ring-2 focus:ring-green-500"
                          />
                          <span className="text-gray-700 font-medium">
                            {symptom.replace(/_/g, " ").replace(/\b\w/g, (c) =>
                              c.toUpperCase()
                            )}
                          </span>
                        </label>

                        {/* CF Slider (tampil jika gejala dicentang) */}
                        {selectedSymptoms[symptom] !== undefined && (
                          <div className="ml-8 mr-4 mb-2 bg-gray-50 p-4 rounded-lg border border-gray-200">
                            <div className="flex justify-between items-center mb-2">
                              <label className="text-sm font-medium text-gray-700">
                                Tingkat Keyakinan
                              </label>
                              <span className="text-sm font-bold text-green-600">
                                {(selectedSymptoms[symptom] * 100).toFixed(0)}%
                              </span>
                            </div>
                            <input
                              type="range"
                              min="0.2"
                              max="1.0"
                              step="0.2"
                              value={selectedSymptoms[symptom]}
                              onChange={(e) =>
                                handleCFChange(symptom, e.target.value)
                              }
                              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                              style={{
                                background: `linear-gradient(to right, #10b981 0%, #10b981 ${
                                  selectedSymptoms[symptom] * 100
                                }%, #e5e7eb ${
                                  selectedSymptoms[symptom] * 100
                                }%, #e5e7eb 100%)`,
                              }}
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                              <span>Tidak Yakin (20%)</span>
                              <span>Sangat Yakin (100%)</span>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Tombol Aksi */}
        <div className="flex gap-4">
          <button
            onClick={runDiagnosis}
            disabled={Object.keys(selectedSymptoms).length === 0 || loading}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white py-3 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Memproses...
              </>
            ) : (
              "🧠 Diagnosis"
            )}
          </button>
          <button
            onClick={resetConsultation}
            className="px-6 bg-gray-200 hover:bg-gray-300 text-gray-800 py-3 rounded-xl font-medium transition-colors"
          >
            🔄 Reset
          </button>
        </div>

        {/* Pesan Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3 mt-4">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-medium text-red-900">Error</div>
              <div className="text-red-800 text-sm">{error}</div>
            </div>
          </div>
        )}
      </div>

      {/* Hasil Diagnosis */}
      {diagnosisResult && (
        <div className="bg-white rounded-2xl shadow-lg p-6 space-y-6">
          {diagnosisResult.conclusions?.length === 0 ? (
            <p className="text-center text-gray-700 py-12">
              Tidak ditemukan diagnosis berdasarkan gejala yang dipilih.
            </p>
          ) : (
            <>
              <div className="flex items-center gap-3 text-green-600">
                <CheckCircle2 className="w-8 h-8" />
                <h3 className="text-2xl font-bold">Diagnosis Selesai!</h3>
              </div>

              {diagnosisResult.conclusions?.map((conclusion, idx) => (
                <div
                  key={idx}
                  className="border-l-4 border-green-500 bg-green-50 rounded-r-xl p-6"
                >
                  <h4 className="text-xl font-bold text-gray-800 mb-4">
                    {idx + 1}. {conclusion.diagnosis}
                  </h4>

                  <div className="mb-4">
                    <div className="text-sm text-gray-600 mb-1">
                      Tingkat Kepercayaan
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-green-500 h-full rounded-full transition-all"
                          style={{ width: `${conclusion.cf * 100}%` }}
                        />
                      </div>
                      <span className="font-bold text-green-600">
                        {(conclusion.cf * 100).toFixed(1)}%
                      </span>
                      <span className="text-sm text-gray-600">
                        ({conclusion.cf_interpretation})
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="bg-white rounded-lg p-4 shadow-sm">
                      <div className="text-sm text-gray-600 mb-1">Pupuk</div>
                      <div className="font-semibold text-gray-800">
                        {conclusion.recommendation.pupuk}
                      </div>
                    </div>
                    <div className="bg-white rounded-lg p-4 shadow-sm">
                      <div className="text-sm text-gray-600 mb-1">Dosis</div>
                      <div className="font-semibold text-gray-800">
                        {conclusion.recommendation.dosis}
                      </div>
                    </div>
                    <div className="col-span-full bg-white rounded-lg p-4 shadow-sm">
                      <div className="text-sm text-gray-600 mb-1">
                        Metode Aplikasi
                      </div>
                      <div className="font-semibold text-gray-800">
                        {conclusion.recommendation.metode}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Tombol Download PDF */}
              <div className="flex justify-end mt-6">
                <button
                  onClick={() => {
                    if (!diagnosisResult.consultation_id) {
                      alert("Consultation ID tidak tersedia");
                      return;
                    }
                    exportPDF(diagnosisResult);
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  📄 Download Laporan PDF
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};


const ReportPage = () => {
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      const loadReport = async () => {
        try {
          setLoading(true);
          const data = await fetchSummaryReport();
          setReport(data);
        } catch (err) {
          console.error("Error loading report:", err);
        } finally {
          setLoading(false);
        }
      };
      loadReport();
    }, []);

    return (
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          📊 Laporan Statistik
        </h2>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-green-600" />
          </div>
        ) : report ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-50 p-6 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Total Konsultasi</div>
              <div className="text-3xl font-bold text-blue-600">
                {report.total_consultations}
              </div>
            </div>

            <div className="bg-green-50 p-6 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Rata-rata CF</div>
              <div className="text-3xl font-bold text-green-600">
                {report.avg_cf_percentage}
              </div>
            </div>

            <div className="bg-purple-50 p-6 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Jenis Diagnosis</div>
              <div className="text-3xl font-bold text-purple-600">
                {report.unique_diagnoses}
              </div>
            </div>

            <div className="col-span-full bg-gray-50 p-6 rounded-lg">
              <div className="text-lg font-semibold mb-2">Diagnosis Terbanyak</div>
              <div className="text-2xl font-bold text-gray-800">
                {report.most_common_diagnosis}
              </div>
              <div className="text-sm text-gray-600">
                {report.most_common_count} kasus
              </div>
            </div>
          </div>
        ) : (
          <p className="text-center text-gray-600 py-12">
            Tidak ada data laporan.
          </p>
        )}
      </div>
    );
  };


    const KnowledgeBasePage = () => {
      return (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">📚 Knowledge Base</h2>
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-6">
            <div className="flex items-start gap-3">
              <Info className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900 mb-2">Tentang Knowledge Base</h3>
                <p className="text-blue-800 text-sm leading-relaxed">
                  Sistem ini menggunakan {rules.length} rules yang telah divalidasi berdasarkan penelitian dari
                  Balai Penelitian Tanaman Sayuran (Balitsa) dan praktisi pertanian berpengalaman.
                </p>
              </div>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-green-600" />
              <span className="ml-3 text-gray-600">Loading rules...</span>
            </div>
          ) : (
            <>
              {rules.length === 0 ? (
                <p className="text-gray-700 text-center py-12">Tidak ada rule yang tersedia.</p>
              ) : (
                <RuleList
                  rules={rules}
                  currentPage={currentPage}
                  itemsPerPage={itemsPerPage}
                  setCurrentPage={setCurrentPage}
                  onDelete={handleDeleteRule}
                  onUpdate={handleUpdateRule}
                />
              )}
            </>
          )}
        </div>
      );
    };

  const RuleList = ({ rules, currentPage, itemsPerPage, setCurrentPage, onDelete, onUpdate }) => {
    const paginatedRules = rules.slice(
      (currentPage - 1) * itemsPerPage,
      currentPage * itemsPerPage
    );
    const totalPages = Math.ceil(rules.length / itemsPerPage);

    return (
      <div className="space-y-4">
        {paginatedRules.map((rule, idx) => (
          <div key={rule.id || idx} className="border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow flex justify-between items-center">
            <div>
              <div className="text-sm text-gray-600 mb-1">Rule {rule.id}</div>
              <div className="font-semibold text-gray-800 text-lg">{rule.diagnosis}</div>
              <div className="text-sm text-gray-600">{rule.antecedents?.length || 0} kondisi</div>
              <div className="text-sm text-gray-600">CF: {(rule.cf * 100).toFixed(0)}%</div>
            </div>
            <div className="flex gap-2">
              {/* <button
                className="bg-yellow-400 hover:bg-yellow-500 text-white rounded px-3 py-1"
                onClick={() => {
                  setEditingRule(rule);
                  setShowEditModal(true);
                }}
              >
                Edit
              </button> */}
              {/* <button
                className="bg-red-500 hover:bg-red-600 text-white rounded px-3 py-1"
                onClick={() => onDelete(rule.id)}
              >
                Delete
              </button> */}
            </div>
          </div>
        ))}

        <div className="flex justify-center gap-4 mt-6">
          <button
            disabled={currentPage === 1}
            className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Prev
          </button>
          <span className="pt-2">Page {currentPage} / {totalPages}</span>
          <button
            disabled={currentPage === totalPages}
            className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </button>
        </div>
      </div>
    );
  };
const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        setLoading(true);
        const data = await fetchHistory();
        setHistory(data);
      } catch (err) {
        console.error("Error loading history:", err);
      } finally {
        setLoading(false);
      }
    };
    loadHistory();
  }, []);

  // Helper function untuk convert history item ke format PDF
  const handleDownload = (item) => {
    try {
      // Parse symptoms jika masih string
      let symptomsList = [];
      if (typeof item.symptoms === 'string') {
        symptomsList = JSON.parse(item.symptoms.replace(/'/g, '"'));
      } else if (Array.isArray(item.symptoms)) {
        symptomsList = item.symptoms;
      }

      // Convert ke format yang dibutuhkan backend
      const pdfData = {
        consultation_id: item.consultation_id || "unknown",
        timestamp: item.timestamp || "",
        symptoms: symptomsList,
        fase: item.fase || "",
        conclusions: [{
          diagnosis: item.diagnosis || "No diagnosis",
          cf: parseFloat(item.cf) || 0.0,
          recommendation: {
            pupuk: "N/A",
            dosis: "N/A",
            metode: "N/A"
          }
        }]
      };
      
      exportPDF(pdfData);
    } catch (err) {
      console.error("Error preparing PDF data:", err);
      alert("Gagal mempersiapkan data untuk PDF");
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        📜 Riwayat Konsultasi
      </h2>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        </div>
      ) : history.length === 0 ? (
        <p className="text-center text-gray-600 py-12">
          Belum ada riwayat konsultasi.
        </p>
      ) : (
        <div className="space-y-4">
          {history.map((item, idx) => (
            <div
              key={idx}
              className="border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="text-sm text-gray-500 mb-1">
                    {item.timestamp ? new Date(item.timestamp).toLocaleString('id-ID') : 'N/A'}
                  </div>
                  <div className="font-semibold text-gray-800 text-lg mb-2">
                    {item.diagnosis || 'Tidak ada diagnosis'}
                  </div>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">ID:</span> {item.consultation_id || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">CF:</span> {((parseFloat(item.cf) || 0) * 100).toFixed(1)}%
                  </div>
                </div>
                <button
                  onClick={() => handleDownload(item)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  📄 Download PDF
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

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
 
const EditRuleModal = ({ rule, onClose, onSave }) => {
  const [formData, setFormData] = useState(rule || {});

  if (!rule) return null;

  // Pastikan rule_id ikut tersimpan (karena backend butuh ini)
  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
      rule_id: rule.rule_id || rule.id, // ✅ pastikan tetap ada
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onSave(formData);
      onClose(); // ✅ Tutup modal setelah berhasil simpan
    } catch (err) {
      console.error("❌ Gagal menyimpan rule:", err);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-2xl p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-800">
          ✏️ Edit Rule {rule.rule_id}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 text-sm mb-1">CF</label>
            <input
              type="number"
              step="0.1"
              value={formData.CF || ""}
              onChange={(e) => handleChange("CF", parseFloat(e.target.value))}
              className="w-full border rounded-lg px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm mb-1">
              Penjelasan
            </label>
            <textarea
              value={formData.explanation || ""}
              onChange={(e) => handleChange("explanation", e.target.value)}
              className="w-full border rounded-lg px-3 py-2"
              rows="3"
            />
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300"
            >
              Batal
            </button>
            <button
              type="submit"
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            >
              Simpan Perubahan
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};



  const menuItems = [
    { id: 'home', label: 'Beranda', icon: Leaf },
    { id: 'consultation', label: 'Konsultasi', icon: FlaskConical },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
    { id: 'history', label: 'Riwayat', icon: Clock }, 
    { id: 'reports', label: 'Laporan', icon: BarChart3 },
    { id: 'about', label: 'Tentang', icon: Info }
  ];

  return (
    
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      <Toaster position="top-right" reverseOrder={false} />
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

          <main className="flex-1">
            {activeMenu === 'home' && <HomePage />}
            {activeMenu === 'consultation' && <ConsultationPage />}
            {activeMenu === 'knowledge' && <KnowledgeBasePage />}
            {activeMenu === 'reports' && <ReportPage />} 
            {activeMenu === 'about' && <AboutPage />}
            {activeMenu === 'history' && <HistoryPage />}
          </main>
        </div>
      </div>

      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600 text-sm">
            © 2025 Sistem Pakar Pemupukan Cabai. Powered by Forward Chaining & Certainty Factor.
          </div>
        </div>
      </footer>
       {showEditModal && editingRule && (
        <EditRuleModal
          rule={editingRule}
          onClose={() => setShowEditModal(false)}
          onSave={handleUpdateRule}
        />
      )}
    </div>
  );
};

export default ExpertSystemUI;