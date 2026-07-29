import api from "./api";

export async function getEmployees(params = {}) {
  const response = await api.get("/employees/", { params });
  return response.data.results;
}

export async function createEmployee(employee) {
  const response = await api.post("/employees/", employee);
  return response.data;
}

export async function updateEmployee(id, employee) {
  const response = await api.patch(`/employees/${id}/`, employee);
  return response.data;
}

export async function updateEmployeeAccess(id, access) {
  const response = await api.patch(`/employees/${id}/access/`, access);
  return response.data;
}

export async function setEmployeePassword(id, newPassword) {
  await api.post(`/employees/${id}/set-password/`, {
    new_password: newPassword,
  });
}

// Временная совместимость со старой страницей администрирования.
export const postEmployee = createEmployee;

export async function deleteEmployee(id) {
  return updateEmployeeAccess(id, {
    is_active: false,
  });
}