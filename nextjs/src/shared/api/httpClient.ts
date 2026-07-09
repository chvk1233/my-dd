import { API_BASE_URL } from "@/shared/config/env";

export async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    throw new Error(`${path} failed`);
  }
  return response.json();
}
