import api from "./api";
import Cookies from "js-cookie";

export const getMeetings = async (employeeId) => {
  const response = await api.get("/reports/?employee_id=" + employeeId);
  return response.data;
};

export const generateReport = async (formData) => {
  const response = await api.post("/ai/v1/generate/", formData);
  return response.data;
};
