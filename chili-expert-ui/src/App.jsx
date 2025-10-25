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
import toast, { Toaster } from 'react-hot-toast';
import cabaiImg from './assets/cabai.avif';
import { 
  PieChart, Pie, Cell, 
  BarChart, Bar, 
  LineChart, Line,  
  XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer 
} from 'recharts';
// Letakkan setelah import, sebelum ExpertSystemUI
const EditRuleModal = ({ rule, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    CF: rule.cf || 0.8,
    explanation: rule.explanation || ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onSave(rule.id, formData);
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Edit Rule {rule.id}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-semibold mb-2">Certainty Factor (CF)</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={formData.CF}
              onChange={(e) => setFormData({...formData, CF: parseFloat(e.target.value)})}
              className="w-full border-2 border-gray-300 rounded-lg px-4 py-2"
            />
          </div>

          <div>
            <label className="block font-semibold mb-2">Explanation</label>
            <textarea
              value={formData.explanation}
              onChange={(e) => setFormData({...formData, explanation: e.target.value})}
              rows="4"
              className="w-full border-2 border-gray-300 rounded-lg px-4 py-2"
            />
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-200 hover:bg-gray-300 px-6 py-2 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

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
  const [showAddModal, setShowAddModal] = useState(false); 

// State dark mode
const [isDarkMode, setIsDarkMode] = useState(() => {
  const saved = localStorage.getItem('darkMode');
  if (saved !== null) {
    return saved === 'true';
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
});


// Effect untuk toggle
useEffect(() => {
  if (isDarkMode) {
    document.documentElement.classList.add('dark');
    localStorage.setItem('darkMode', 'true');
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('darkMode', 'false');
  }
}, [isDarkMode]);

// Toggle function
  const toggleDarkMode = () => {
    console.log('🌓 Toggle clicked! Current:', isDarkMode, '→ New:', !isDarkMode); // ← DEBUG 4
    setIsDarkMode(!isDarkMode);
  };



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
  // Validasi: Pilih minimal 1 gejala
  const facts = Object.keys(selectedSymptoms);
  
  // ✅ TAMBAH: Toast validation untuk gejala
  if (facts.length === 0) {
    toast.error('⚠️ Pilih minimal satu gejala!');
    return;
  }

  // ✅ TAMBAH: Toast validation untuk fase
  if (!selectedPhase.vegetatif && !selectedPhase.generatif) {
    toast.error('⚠️ Pilih fase pertumbuhan!');
    return;
  }

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

  // ✅ TAMBAH: Loading toast
  const loadingToast = toast.loading('🔍 Sedang menganalisis...');

  try {
    setLoading(true);
    const response = await diagnose(facts, user_cfs);
    setDiagnosisResult(response);
    
    // ✅ TAMBAH: Success toast
    toast.dismiss(loadingToast);
    toast.success('✅ Diagnosis berhasil!');
    
  } catch (err) {
    setError(err.message);
    
    // ✅ TAMBAH: Error toast
    toast.dismiss(loadingToast);
    toast.error('❌ Gagal melakukan diagnosis: ' + err.message);
    
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
  if (!confirm(`Yakin ingin menghapus Rule ${ruleId}?`)) {
    return;
  }

  const loadingToast = toast.loading('Menghapus rule...'); // ✅ Loading state

  try {
    await deleteRule(ruleId);
    
    // Refresh rules
    const refreshedRules = await fetchRules();
    setRules(refreshedRules);
    
    toast.success(`✅ Rule ${ruleId} berhasil dihapus`, { 
      id: loadingToast // Replace loading toast
    });
  } catch (err) {
    toast.error(`❌ Gagal menghapus: ${err.message}`, {
      id: loadingToast
    });
    console.error(err);
  }
};

// ✅ OPEN ADD MODAL
const handleAddRule = () => {
  setEditingRule(null); // Reset editing state
  setShowAddModal(true);
};

// ✅ OPEN EDIT MODAL
const handleEditRule = (rule) => {
  setEditingRule(rule);
  setShowEditModal(true);
};

// ✅ SAVE NEW RULE
const handleSaveNewRule = async (ruleData) => {
  try {
    // Kirim data ke backend
    const response = await fetch('http://localhost:5000/api/rules', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify(ruleData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }

    // Ambil ulang rules terbaru dari backend
    const refreshedRules = await fetchRules();

    // Update state rules agar UI diperbarui
    setRules(refreshedRules);

    toast.success('Rule berhasil ditambahkan');

    setShowAddModal(false);

  } catch (err) {
    toast.error('Gagal menambahkan rule: ' + err.message);
  }
}


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
const HomePage = () => {
  // State
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load rules
  useEffect(() => {
    const loadRules = async () => {
      try {
        const data = await fetchRules();
        const rulesArray = Array.isArray(data)
          ? data
          : Object.entries(data).map(([id, rule]) => ({ id, ...rule }));
        setRules(rulesArray);
      } catch (err) {
      console.error(err);
      setRules([]);
      // ✅ TAMBAH: Error toast
      toast.error('❌ Gagal memuat data rules');
    } finally {
      setLoading(false);
    }
  };
  loadRules();
}, []);

  // Data preparation untuk Pie Chart
  const diagnosisData = rules.reduce((acc, rule) => {
    const diagnosis = rule.consequent || 'Unknown';
    const existing = acc.find(item => item.name === diagnosis);
    if (existing) {
      existing.value += 1;
    } else {
      acc.push({ name: diagnosis, value: 1 });
    }
    return acc;
  }, []);

  // Data preparation untuk Bar Chart
  const cfData = [
    {
      category: 'Nitrogen',
      avgCF: rules
        .filter(r => r.consequent?.toLowerCase().includes('nitrogen'))
        .reduce((sum, r) => sum + (r.cf || 0), 0) / 
        rules.filter(r => r.consequent?.toLowerCase().includes('nitrogen')).length || 0
    },
    {
      category: 'Fosfor',
      avgCF: rules
        .filter(r => r.consequent?.toLowerCase().includes('fosfor'))
        .reduce((sum, r) => sum + (r.cf || 0), 0) / 
        rules.filter(r => r.consequent?.toLowerCase().includes('fosfor')).length || 0
    },
    {
      category: 'Kalium',
      avgCF: rules
        .filter(r => r.consequent?.toLowerCase().includes('kalium'))
        .reduce((sum, r) => sum + (r.cf || 0), 0) / 
        rules.filter(r => r.consequent?.toLowerCase().includes('kalium')).length || 0
    },
  ].filter(d => d.avgCF > 0);

  // Data preparation untuk Line Chart
  const cfRangeData = [
    { range: '0-20%', count: rules.filter(r => r.cf <= 0.2).length },
    { range: '21-40%', count: rules.filter(r => r.cf > 0.2 && r.cf <= 0.4).length },
    { range: '41-60%', count: rules.filter(r => r.cf > 0.4 && r.cf <= 0.6).length },
    { range: '61-80%', count: rules.filter(r => r.cf > 0.6 && r.cf <= 0.8).length },
    { range: '81-100%', count: rules.filter(r => r.cf > 0.8).length },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  return (
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
          { 
            label: 'Total Rules', 
            value: rules.length.toString(), 
            icon: BookOpen, 
            color: 'bg-blue-500' 
          },
          { 
            label: 'Diagnosis Unik', 
            value: diagnosisData.length.toString(), 
            icon: FlaskConical, 
            color: 'bg-green-500' 
          },
          { 
            label: 'Avg CF', 
            value: (rules.reduce((sum, r) => sum + (r.cf || 0), 0) / rules.length || 0).toFixed(2), 
            icon: BarChart3, 
            color: 'bg-purple-500' 
          },
          { 
            label: 'Total Nutrisi', 
            value: '8', 
            icon: Sprout, 
            color: 'bg-orange-500' 
          }
        ].map((stat, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
              <stat.icon className="w-6 h-6 text-white" />
            </div>
            <div className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-1">{stat.value}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Data Visualization Section */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 transition-colors">
        {/* Pie Chart - Distribusi Diagnosis */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">📊 Distribusi Diagnosis</h3>
          {loading ? (
            <div className="h-64 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-green-600" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={diagnosisData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name.split(' ')[0]}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {diagnosisData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Bar Chart - Average CF per Kategori */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">📈 Average CF per Kategori</h3>
          {loading ? (
            <div className="h-64 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-green-600" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={cfData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis domain={[0, 1]} />
                <Tooltip formatter={(value) => (value * 100).toFixed(0) + '%'} />
                <Legend />
                <Bar dataKey="avgCF" fill="#10b981" name="Avg Certainty Factor" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Line Chart - CF Range Distribution */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">📉 Distribusi CF Range</h3>
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-green-600" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={cfRangeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="count" 
                stroke="#8884d8" 
                strokeWidth={2}
                name="Jumlah Rules"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
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
};


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
      console.error('Error loading symptoms:', err);
      setError('Gagal memuat data gejala');
      // ✅ TAMBAH: Error toast
      toast.error('❌ Gagal memuat data gejala');
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
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors">
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
            className="border-l-4 border-green-500 bg-green-50 rounded-r-xl p-6 space-y-4"
          >
            <h4 className="text-xl font-bold text-gray-800 mb-4">
              {idx + 1}. {conclusion.diagnosis}
            </h4>

            {/* CF Progress Bar */}
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

            {/* Recommendation Cards */}
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

            {/* ✅ EXPLANATION SECTION */}
            <div className="space-y-3 mt-6">
              {/* HOW Explanation */}
              {conclusion.how_explanation && (
                <details className="bg-white rounded-lg p-4 shadow-sm border-2 border-blue-200 hover:border-blue-400 transition-colors">
                  <summary className="font-semibold text-gray-800 cursor-pointer flex items-center gap-2 hover:text-blue-600 transition-colors">
                    <Info className="w-5 h-5 text-blue-600" />
                    🔍 Bagaimana sistem sampai pada kesimpulan ini?
                  </summary>
                  
                  <div className="mt-4 space-y-4">
                    {/* Natural language explanation */}
                    {conclusion.how_explanation.answer && (
                      <div className="text-sm text-gray-700 bg-blue-50 rounded-lg p-4 border border-blue-200 whitespace-pre-line">
                        {conclusion.how_explanation.answer}
                      </div>
                    )}

                    {/* Reasoning steps */}
                    {conclusion.how_explanation.steps && conclusion.how_explanation.steps.length > 0 && (
                      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border-2 border-blue-200">
                        <h5 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                          <ChevronRight className="w-4 h-4" />
                          📋 Langkah-langkah Penalaran:
                        </h5>
                        {conclusion.how_explanation.steps.map((step, i) => (
                          <div key={i} className="mb-3 pb-3 border-b border-blue-300 last:border-0 bg-white rounded-lg p-3 shadow-sm">
                            <div className="font-medium text-blue-800 mb-2 flex items-center gap-2">
                              <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">
                                {step.step_number}
                              </span>
                              Rule {step.rule_id}
                            </div>
                            <div className="text-sm text-blue-700 ml-8 space-y-1">
                              <div>
                                <strong className="text-blue-900">IF:</strong> {step.if_conditions.join(' AND ')}
                              </div>
                              <div>
                                <strong className="text-blue-900">THEN:</strong> {step.then_conclusion}
                              </div>
                              <div>
                                <strong className="text-blue-900">CF:</strong> 
                                <span className="font-semibold text-green-600 ml-1">{step.cf_percentage}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Rules used */}
                    {conclusion.how_explanation.rules_used && conclusion.how_explanation.rules_used.length > 0 && (
                      <div className="bg-yellow-50 rounded-lg p-3 border-2 border-yellow-200">
                        <strong className="text-yellow-900 flex items-center gap-2">
                          <BookOpen className="w-4 h-4" />
                          📜 Rules yang digunakan:
                        </strong>
                        <div className="text-sm text-yellow-800 mt-2 font-mono font-semibold">
                          {conclusion.how_explanation.rules_used.join(', ')}
                        </div>
                      </div>
                    )}
                  </div>
                </details>
              )}

              {/* Rule Details */}
              {conclusion.rule_details && (
                <details className="bg-white rounded-lg p-4 shadow-sm border-2 border-purple-200 hover:border-purple-400 transition-colors">
                  <summary className="font-semibold text-gray-800 cursor-pointer flex items-center gap-2 hover:text-purple-600 transition-colors">
                    <BookOpen className="w-5 h-5 text-purple-600" />
                    📖 Detail Rule {conclusion.rule_id || 'N/A'}
                  </summary>
                  
                  <div className="mt-4 space-y-3">
                    {/* Natural language rule */}
                    {conclusion.rule_details.natural_language && (
                      <div className="text-sm text-gray-700 bg-purple-50 rounded-lg p-4 border-2 border-purple-200 whitespace-pre-line">
                        {conclusion.rule_details.natural_language}
                      </div>
                    )}

                    {/* CF Interpretation */}
                    {conclusion.rule_details.certainty_factor && (
                      <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-200">
                        <strong className="text-indigo-900">📊 Tingkat Kepercayaan:</strong>
                        <div className="text-sm text-indigo-800 mt-1">
                          {conclusion.rule_details.certainty_factor.percentage} - {conclusion.rule_details.certainty_factor.interpretation}
                        </div>
                      </div>
                    )}

                    {/* Expert explanation */}
                    {conclusion.rule_details.expert_explanation && (
                      <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
                        <strong className="text-green-900 flex items-center gap-2 mb-2">
                          <Sprout className="w-4 h-4" />
                          👨‍🌾 Penjelasan Pakar:
                        </strong>
                        <div className="text-sm text-green-800 leading-relaxed">
                          {conclusion.rule_details.expert_explanation}
                        </div>
                      </div>
                    )}
                  </div>
                </details>
              )}
            </div>
          </div>
        ))}

        {/* Comparison Section (jika multiple conclusions) */}
        {diagnosisResult.comparison && diagnosisResult.conclusions.length > 1 && (
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-300 rounded-xl p-6 mt-6">
            <h3 className="text-lg font-bold text-blue-900 mb-3 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              📊 Perbandingan Diagnosis
            </h3>
            <div className="text-blue-800 whitespace-pre-line leading-relaxed">
              {diagnosisResult.comparison.summary}
            </div>
          </div>
        )}

        {/* Tombol Download PDF */}
        <div className="flex justify-end mt-6 pt-6 border-t-2 border-gray-200">
          <button
            onClick={() => {
              if (!diagnosisResult.consultation_id) {
                toast.error("❌ Consultation ID tidak tersedia");
                return;
              }
              exportPDF(diagnosisResult);
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors shadow-md hover:shadow-lg flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download Laporan PDF
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
      console.error('Error loading report:', err);
      // ✅ TAMBAH: Error toast
      toast.error('❌ Gagal memuat laporan statistik');
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
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Load rules
  useEffect(() => {
   const loadRules = async () => {
  try {
    setLoading(true);
    const data = await fetchRules();
    
    // ✅ Lihat detail isi first rule
    console.log("🔍 RAW data from API:", data);
    console.log("🔍 First rule DETAIL:", JSON.stringify(data[0], null, 2));
    
    const rulesArray = Array.isArray(data)
      ? data
      : Object.entries(data).map(([id, rule]) => ({ 
          id, 
          ...rule 
        }));
    
    console.log("🔍 Converted array:", rulesArray);
    console.log("🔍 First rule in array DETAIL:", JSON.stringify(rulesArray[0], null, 2));
    
    setRules(rulesArray);
  } catch (err) {
      console.error("Error loading rules:", err);
      setRules([]);
      // ✅ TAMBAH: Error toast
      toast.error('❌ Gagal memuat data knowledge base');
    } finally {
      setLoading(false);
    }
  };
  loadRules();
}, []);

  // ✅ Filter logic
const filteredRules = rules.filter(rule => {
  const matchesSearch = 
    rule.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    rule.consequent?.toLowerCase().includes(searchQuery.toLowerCase()) || // ✅ Ganti dari diagnosis
    rule.antecedents?.some(symptom => symptom.toLowerCase().includes(searchQuery.toLowerCase())) || // ✅ Ganti dari IF
    rule.recommendation?.pupuk?.toLowerCase().includes(searchQuery.toLowerCase()); // ✅ Ganti dari THEN.pupuk

  const matchesCategory = 
    filterCategory === 'all' || 
    rule.consequent?.toLowerCase().includes(filterCategory.toLowerCase()); // ✅ Ganti dari THEN.diagnosis

  return matchesSearch && matchesCategory;
});

  // Pagination for filtered results
  const paginatedRules = filteredRules.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );
  const totalPages = Math.ceil(filteredRules.length / itemsPerPage);
  
  const highlightText = (text, query) => {
    if (!query || !text) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">{part}</mark>
      ) : (
        part
      )
    );
  };
  // Reset to page 1 when search/filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, filterCategory]);

  // Delete handler (if you have it)
  const handleDeleteRule = async (ruleId) => {
    if (!confirm(`Hapus rule ${ruleId}?`)) return;
    try {
      // await deleteRule(ruleId);
      // await loadRules();
     toast.info('ℹ️ Delete feature coming soon!', {
      icon: 'ℹ️',
      style: {
        background: '#dbeafe',
        color: '#1e40af',
      }
    });
    } catch (err) {
      console.error("Error deleting rule:", err);
    }
  };

  // Update handler (if you have it)
  const handleUpdateRule = (rule) => {
  toast.info('ℹ️ Update feature coming soon!', {
    icon: 'ℹ️',
    style: {
      background: '#dbeafe',
      color: '#1e40af',
    }
  });
};

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          📚 Knowledge Base ({filteredRules.length}/{rules.length})
        </h2>
        <button
          onClick={handleAddRule}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 shadow-md hover:shadow-lg"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add New Rule
        </button>
      </div>


      {/* ✅ Search & Filter Section */}
      <div className="bg-gray-50 rounded-xl p-6 mb-6 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <input
            type="text"
            placeholder="🔍 Cari berdasarkan ID, gejala, diagnosis, atau pupuk..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full p-3 pl-10 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
          />
          <span className="absolute left-3 top-3.5 text-gray-400 text-xl">🔍</span>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 font-bold text-xl"
            >
              ✕
            </button>
          )}
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterCategory('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterCategory === 'all'
                ? 'bg-green-600 text-white shadow-md'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            🌱 Semua
          </button>
          <button
            onClick={() => setFilterCategory('nitrogen')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterCategory === 'nitrogen'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            💧 Nitrogen (N)
          </button>
          <button
            onClick={() => setFilterCategory('fosfor')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterCategory === 'fosfor'
                ? 'bg-purple-600 text-white shadow-md'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            ⚡ Fosfor (P)
          </button>
          <button
            onClick={() => setFilterCategory('kalium')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterCategory === 'kalium'
                ? 'bg-orange-600 text-white shadow-md'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            🔥 Kalium (K)
          </button>
        </div>

        {/* Results Count */}
        {(searchQuery || filterCategory !== 'all') && (
          <div className="text-sm text-gray-600 flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
            Menampilkan <strong>{filteredRules.length}</strong> dari <strong>{rules.length}</strong> total rules
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
          <span className="ml-3 text-gray-600">Loading rules...</span>
        </div>
      ) : filteredRules.length === 0 ? (
        /* Empty State */
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <p className="text-gray-500 text-lg mb-2">
            {searchQuery 
              ? `❌ Tidak ada rules yang cocok dengan "${searchQuery}"` 
              : '📦 Tidak ada rules'}
          </p>
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                setFilterCategory('all');
              }}
              className="text-green-600 hover:text-green-700 font-medium"
            >
              Reset pencarian
            </button>
          )}
        </div>
      ) : (
        /* Rules List */
        <>
       <div className="grid gap-4">
  {paginatedRules.map((rule) => (
    <div 
      key={rule.id} 
      className="bg-white rounded-xl shadow-md p-6 border-2 border-gray-200 hover:shadow-lg hover:border-green-300 transition-all"
    >
      <div className="flex justify-between items-start">
        {/* Left: Rule Info */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-bold">
              {rule.id}
            </span>
            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
              CF: {(rule.cf * 100).toFixed(0)}%
            </span>
          </div>

          <h3 className="text-lg font-bold text-gray-800 mb-2">
            {highlightText(rule.consequent, searchQuery)}
          </h3>

          <div className="text-sm text-gray-600 mb-2">
            <strong>IF:</strong> {rule.antecedents?.length || 0} kondisi
          </div>

          {rule.explanation && (
            <div className="text-sm text-gray-600 italic bg-gray-50 p-3 rounded-lg mt-2">
              "{rule.explanation.substring(0, 150)}{rule.explanation.length > 150 ? '...' : ''}"
            </div>
          )}
        </div>

        {/* Right: Action Buttons */}
        <div className="flex flex-col gap-2 ml-4">
          <button
            onClick={() => handleEditRule(rule)}
            className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2 shadow-md"
            title="Edit Rule"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit
          </button>
          <button
            onClick={() => handleDeleteRule(rule.id)}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2 shadow-md"
            title="Delete Rule"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        </div>
      </div>
    </div>
  ))}
</div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2 mt-6">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-300 transition-colors"
              >
                ← Previous
              </button>
              <span className="text-gray-600">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-300 transition-colors"
              >
                Next →
              </button>
            </div>
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
      console.error('Error loading history:', err);
      // ✅ TAMBAH: Error toast
      toast.error('❌ Gagal memuat riwayat konsultasi');
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
      toast.success('📄 PDF berhasil di-download!');
    
    } catch (err) {
      console.error("Error preparing PDF data:", err);
      toast.error("❌ Gagal mempersiapkan data untuk PDF");
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
 
// ✅ ADD RULE MODAL - NEW COMPONENT
const AddRuleModal = ({ onClose, onSave }) => {
  const [formData, setFormData] = useState({
   
    IF: [],
    THEN: {
      diagnosis: '',
      pupuk: '',
      dosis: '',
      metode: ''
    },
    CF: 0.8,
    explanation: ''
  });
  const [newCondition, setNewCondition] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleThenChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      THEN: {
        ...prev.THEN,
        [field]: value
      }
    }));
  };

  const addCondition = () => {
    if (newCondition.trim()) {
      setFormData(prev => ({
        ...prev,
        IF: [...prev.IF, newCondition.trim()]
      }));
      setNewCondition('');
    }
  };

  const removeCondition = (index) => {
    setFormData(prev => ({
      ...prev,
      IF: prev.IF.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  
  // ✅ VALIDATION (tanpa rule_id karena auto-generated)
  if (formData.IF.length === 0) {
    toast.error('❌ Minimal 1 kondisi IF harus ada!');
    return;
  }
  
  if (!formData.THEN.diagnosis || !formData.THEN.diagnosis.trim()) {
    toast.error('❌ Diagnosis wajib diisi!');
    return;
  }

  if (!formData.THEN.pupuk || !formData.THEN.pupuk.trim()) {
    toast.error('❌ Pupuk wajib diisi!');
    return;
  }

  if (!formData.THEN.dosis || !formData.THEN.dosis.trim()) {
    toast.error('❌ Dosis wajib diisi!');
    return;
  }

  if (!formData.THEN.metode || !formData.THEN.metode.trim()) {
    toast.error('❌ Metode aplikasi wajib diisi!');
    return;
  }

  setIsSubmitting(true);
  try {
    await onSave(formData);
  } catch (err) {
    console.error('Error saving rule:', err);
    toast.error('❌ Gagal menyimpan: ' + err.message);
  } finally {
    setIsSubmitting(false);
  }
};


  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-green-600 to-emerald-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add New Rule
            </h2>
            <button
              onClick={onClose}
              className="hover:bg-white/20 rounded-full p-2 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
        
          {/* Info Box - Auto-generated ID */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 text-blue-800">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">Rule ID akan dibuat otomatis oleh sistem</span>
          </div>
        </div>

          {/* IF Conditions */}
          <div className="bg-blue-50 rounded-xl p-4 border-2 border-blue-200">
            <label className="block text-gray-800 font-bold mb-3">
              IF Conditions <span className="text-red-500">*</span>
            </label>
            
            {/* Condition List */}
            <div className="space-y-2 mb-3">
              {formData.IF.map((condition, index) => (
                <div key={index} className="flex items-center gap-2 bg-white rounded-lg p-3 border border-blue-300">
                  <span className="flex-1 text-gray-800">{index + 1}. {condition}</span>
                  <button
                    type="button"
                    onClick={() => removeCondition(index)}
                    className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg transition-colors"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>

            {/* Add Condition Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={newCondition}
                onChange={(e) => setNewCondition(e.target.value)}
                placeholder="daun_kuning_merata"
                className="flex-1 border-2 border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addCondition();
                  }
                }}
              />
              <button
                type="button"
                onClick={addCondition}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Add Condition
              </button>
            </div>
          </div>

          {/* THEN Consequent */}
          <div className="bg-green-50 rounded-xl p-4 border-2 border-green-200 space-y-4">
            <label className="block text-gray-800 font-bold mb-2">
              THEN Consequent <span className="text-red-500">*</span>
            </label>

            <div>
              <label className="block text-gray-700 font-medium mb-1">Diagnosis</label>
              <input
                type="text"
                value={formData.THEN.diagnosis}
                onChange={(e) => handleThenChange('diagnosis', e.target.value)}
                placeholder="Kekurangan Nitrogen (N)"
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 font-medium mb-1">Pupuk</label>
                <input
                  type="text"
                  value={formData.THEN.pupuk}
                  onChange={(e) => handleThenChange('pupuk', e.target.value)}
                  placeholder="Urea atau ZA"
                  className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-1">Dosis</label>
                <input
                  type="text"
                  value={formData.THEN.dosis}
                  onChange={(e) => handleThenChange('dosis', e.target.value)}
                  placeholder="150-200 kg/ha"
                  className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-1">Metode Aplikasi</label>
              <input
                type="text"
                value={formData.THEN.metode}
                onChange={(e) => handleThenChange('metode', e.target.value)}
                placeholder="Kocor atau tabur"
                className="w-full border-2 border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          {/* CF */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Certainty Factor (CF)
            </label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={formData.CF}
              onChange={(e) => handleChange('CF', parseFloat(e.target.value))}
              className="w-full border-2 border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-green-500"
            />
            <div className="text-sm text-gray-600 mt-1">
              Current: {(formData.CF * 100).toFixed(0)}%
            </div>
          </div>

          {/* Explanation */}
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Explanation
            </label>
            <textarea
              value={formData.explanation}
              onChange={(e) => handleChange('explanation', e.target.value)}
              placeholder="Penjelasan pakar tentang rule ini..."
              rows="4"
              className="w-full border-2 border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-green-500"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t-2 border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-semibold transition-colors"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Save Rule
                </>
              )}
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
    
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors">

      <Toaster 
      position="top-right"
      reverseOrder={false}
      toastOptions={{
        duration: 3000,
        style: {
          background: '#fff',
          color: '#1f2937',
          padding: '16px',
          borderRadius: '10px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          fontSize: '14px',
          fontWeight: '500',
        },
        success: {
          duration: 3000,
          iconTheme: {
            primary: '#10b981',
            secondary: '#fff',
          },
          style: {
            background: '#ecfdf5',
            color: '#065f46',
            border: '1px solid #10b981',
          },
        },
        error: {
          duration: 4000,
          iconTheme: {
            primary: '#ef4444',
            secondary: '#fff',
          },
          style: {
            background: '#fef2f2',
            color: '#991b1b',
            border: '1px solid #ef4444',
          },
        },
        loading: {
          iconTheme: {
            primary: '#3b82f6',
            secondary: '#fff',
          },
        },
      }}
    />
   
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Leaf className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="font-bold text-gray-800 dark:text-gray-100 text-lg transition-colors">Sistem Pakar</div>
                <div className="text-xs text-gray-600 dark:text-gray-400 transition-colors">Pemupukan Cabai</div>

              </div>
            </div>
            <button
        onClick={toggleDarkMode}
        className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      >
        {isDarkMode ? (
          // Sun icon
          <svg className="w-5 h-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        ) : (
          // Moon icon
          <svg className="w-5 h-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        )}
      </button>
          </div>
        </div>
      </header>

         

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          <aside className="lg:w-64 flex-shrink-0">
            <nav className="bg-white dark:bg-gray-800 rounded-2xl shadow-md p-4 space-y-2 sticky top-24 transition-colors">
              {menuItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => setActiveMenu(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
                    activeMenu === item.id
                      ? 'bg-green-600 text-white shadow-md'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
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
       {/* ✅ RENDER MODALS - TAMBAH INI */}
      {showEditModal && editingRule && (
        <EditRuleModal
          rule={editingRule}
          onClose={() => setShowEditModal(false)}
          onSave={handleUpdateRule}
        />
      )}

      {showAddModal && (
        <AddRuleModal
          onClose={() => setShowAddModal(false)}
          onSave={handleSaveNewRule}
        />
      )}
    </div>
  );
};

export default ExpertSystemUI;
