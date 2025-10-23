// src/api/api.js
// Helper functions to connect React frontend to Flask backend

const BASE_URL = "http://localhost:5000/api";

export async function fetchSymptoms() {
  const res = await fetch(`${BASE_URL}/symptoms`);
  if (!res.ok) throw new Error("Failed to fetch symptoms");
  return res.json();
}

export async function diagnose(symptoms, fase) {
  const res = await fetch(`${BASE_URL}/diagnose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symptoms, fase })
  });
  if (!res.ok) throw new Error("Failed to diagnose");
  return res.json();
}

export async function fetchRules() {
  const res = await fetch(`${BASE_URL}/rules`);
  if (!res.ok) throw new Error("Failed to fetch rules");
  return res.json();
}

// Add more API helpers as needed
