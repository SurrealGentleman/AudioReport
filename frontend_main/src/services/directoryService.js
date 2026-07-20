import api from "./api";

export async function getDepartments(params = {}) {
  const response = await api.get("/departments/", { params });
  return response.data.results;
}

export async function createDepartment(name) {
  const response = await api.post("/departments/", { name });
  return response.data;
}

export async function deleteDepartment(id) {
  await api.delete(`/departments/${id}/`);
}

export async function getPositions(params = {}) {
  const response = await api.get("/positions/", { params });
  return response.data.results;
}

export async function createPosition(name) {
  const response = await api.post("/positions/", { name });
  return response.data;
}

export async function deletePosition(id) {
  await api.delete(`/positions/${id}/`);
}