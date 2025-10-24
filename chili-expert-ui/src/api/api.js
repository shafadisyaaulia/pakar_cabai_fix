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

export async function fetchRules() {
  const res = await fetch(`${BASE_URL}/rules`);
  if (!res.ok) throw new Error("Failed to fetch rules");
  return await res.json();
}

// ==========================
// Diagnosis Endpoint
// ==========================

export async function diagnose(symptoms, fase) {
  const payload = { symptoms, fase };
  const res = await fetch(`${BASE_URL}/diagnose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
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
