import api from "./api";

export async function getTasks() {
  const response = await api.get("/tasks/");
  return response.data.results;
}

export async function patchTask(taskId, status) {
  const response = await api.patch(`/tasks/${taskId}/`, {
    status,
  });

  return response.data;
}