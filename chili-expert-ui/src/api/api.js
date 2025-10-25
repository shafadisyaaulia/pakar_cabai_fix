// src/api/api.js
// Helper functions to connect React frontend with Flask backend

const BASE_URL = "http://localhost:5000/api";

// ==========================
// Basic Data Fetching
// ==========================

export async function fetchSymptoms() {
  const res = await fetch(`${BASE_URL}/symptoms`);
  if (!res.ok) throw new Error("Failed to fetch symptoms");
  return await res.json();
}

export const fetchRules = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/rules');
    const data = await response.json();
    
    console.log('🔍 fetchRules response:', data); // ← DEBUG
    console.log('📊 Rules count:', data.length); // ← DEBUG
    
    return data;
  } catch (error) {
    console.error('Error fetching rules:', error);
    throw error;
  }
};


// ==========================
// Diagnosis Endpoint
// ==========================

export async function diagnose(symptoms, fase, userCFs = {}) {
  const res = await fetch(`${BASE_URL}/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      symptoms, 
      fase,
      user_cfs: userCFs  
    })
  });
  if (!res.ok) throw new Error("Failed to diagnose");
  return await res.json();
}

// ==========================
// Knowledge Base CRUD
// ==========================

// Add new rule
export async function addRule(ruleData) {
  const res = await fetch(`${BASE_URL}/rules`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ruleData)
  });
  if (!res.ok) throw new Error("Failed to add rule");
  return await res.json();
}

// Update existing rule
export async function updateRule(ruleId, updateData) {
  const res = await fetch(`${BASE_URL}/rules/${ruleId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updateData)
  });
  if (!res.ok) throw new Error("Failed to update rule");
  return await res.json();
}

// Delete rule
export async function deleteRule(ruleId) {
  const res = await fetch(`${BASE_URL}/rules/${ruleId}`, {
    method: "DELETE"
  });
  if (!res.ok) throw new Error("Failed to delete rule");
  return await res.json();
}

// ==========================
// Analytics or Statistics
// ==========================

export async function fetchStatistics() {
  const res = await fetch(`${BASE_URL}/statistics`);
  if (!res.ok) throw new Error("Failed to fetch statistics");
  return await res.json();
}

// ==========================
// Consultation History
// ==========================

export async function fetchHistory() {
  const res = await fetch(`${BASE_URL}/history`);
  if (!res.ok) throw new Error("Failed to fetch consultation history");
  return await res.json();
}

// ==========================
// Health Check
// ==========================

export async function healthCheck() {
  const res = await fetch(`${BASE_URL.replace("/api", "")}/health`);
  if (!res.ok) throw new Error("Server health check failed");
  return await res.json();
}




// Export PDF
export async function exportPDF(diagnosisData) {
  try {
    const res = await fetch(`${BASE_URL}/export/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(diagnosisData)
    });
    
    if (!res.ok) throw new Error("Failed to export PDF");
    
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `laporan_diagnosis_${diagnosisData.consultation_id}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Error exporting PDF:", err);
    alert("Gagal download PDF");
  }
}

// Get summary report
export async function fetchSummaryReport() {
  const res = await fetch(`${BASE_URL}/reports/summary`);
  if (!res.ok) throw new Error("Failed to fetch report");
  return await res.json();
}

// Get top diagnoses
export async function fetchTopDiagnoses(topN = 5) {
  const res = await fetch(`${BASE_URL}/reports/top-diagnoses?top=${topN}`);
  if (!res.ok) throw new Error("Failed to fetch top diagnoses");
  return await res.json();
}


