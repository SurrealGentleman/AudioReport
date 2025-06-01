import api from "./api";

export const getPosts = async () => {
  const response = await api.get("/posts/");
  return response.data;
};

export const postPosts = async (name) => {
  const response = await api.post("/posts/", { name: name });
  return response.data;
};

export const deletePost = async (postId) => {
  const response = await api.delete("/posts/" + postId + "/");
  return response.data;
};
