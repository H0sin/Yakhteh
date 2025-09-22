import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8001/api/v1",
  timeout: 5000,
});

// Attach token from localStorage (if present) to each request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("yakhteh_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(email: string, password: string) {
  const res = await apiClient.post("/auth/login", { email, password });
  return res.data;
}

export async function register(fullName: string, email: string, password: string, workspaceName: string) {
  const payload = {
    full_name: fullName,
    email,
    password,
    workspace_name: workspaceName,
  };
  const res = await apiClient.post("/auth/register", payload);
  return res.data;
}

export default apiClient;