import api from "./api";
import Cookies from "js-cookie";

export const getTasks = async (employeeId) => {
  const response = await api.get("/tasks/?employee_id=" + employeeId);
  return response.data;
};

export const patchTask = async (taskId, status) => {
  const response = await api.patch("/tasks/" + taskId + "/", {
    status: status,
  });
  return response.data;
};
