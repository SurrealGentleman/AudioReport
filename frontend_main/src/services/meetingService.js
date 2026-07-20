import api from "./api";

export async function getMeetings(params = {}) {
  const response = await api.get("/reports/", { params });
  return response.data.results;
}

export async function generateReport(formData) {
  const response = await api.post("/ai/generate/", formData);
  return response.data;
}

export async function saveReport(report) {
  const response = await api.post("/reports/save/", report);
  return response.data;
}