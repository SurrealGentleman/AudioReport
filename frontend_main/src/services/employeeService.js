import api from "./api";

export const getEmployees = async (params) => {
  const response = await api.get("/employees/", { params });
  return response.data;
};

export const postEmployee = async (dataJson) => {
  const response = await api.post("/employees/", dataJson);
  return response.data;
};

export const deleteEmployee = async (employeeId) => {
  const response = await api.delete("/employees/" + employeeId + "/");
  return response.data;
};
