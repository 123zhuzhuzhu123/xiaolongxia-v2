/* API 客户端。MVP 阶段不带认证，直接调用 V2 后端。 */
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export async function fetchProjects() {
  const res = await api.get("/projects");
  return res.data;
}

export async function fetchContents(projectId: number, limit = 100) {
  const res = await api.get(`/contents?project_id=${projectId}&limit=${limit}`);
  return res.data;
}

export async function fetchCreators(projectId: number) {
  const res = await api.get(`/creators?project_id=${projectId}`);
  return res.data;
}

export async function createProject(name: string, description?: string) {
  const res = await api.post("/projects", { name, description });
  return res.data;
}

export async function fetchSkus(projectId: number) {
  const res = await api.get(`/copywriter/skus?project_id=${projectId}`);
  return res.data;
}

export async function fetchCopyDrafts(projectId: number) {
  const res = await api.get(`/copy/drafts?project_id=${projectId}`);
  return res.data;
}

export async function generateCopy(contentId: number, projectId: number, skuId?: number | null) {
  const res = await api.post(`/copy/generate/${contentId}`, {
    project_id: projectId,
    sku_id: skuId,
  });
  return res.data;
}

export async function scoreCopyVersion(versionId: number) {
  const res = await api.post(`/copy/versions/${versionId}/score`);
  return res.data;
}

export async function generateStoryboard(versionId: number) {
  const res = await api.post(`/copy/versions/${versionId}/storyboard`);
  return res.data;
}

export async function selectCopyVersion(versionId: number) {
  const res = await api.post(`/copy/versions/${versionId}/select`);
  return res.data;
}
