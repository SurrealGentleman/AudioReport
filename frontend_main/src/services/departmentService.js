import api from "./api";
import Cookies from "js-cookie";

export const getDepartments = async () => {
  const response = await api.get("/departments/");
  return response.data;
};

export const postDepartment = async (name) => {
  const response = await api.post("/departments/", { name: name });
  return response.data;
};

export const deleteDepartment = async (departmentId) => {
  const response = await api.delete("/departments/" + departmentId + "/");
  return response.data;
};
