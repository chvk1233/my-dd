import type { EventsResponse } from "./types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:5000";

export async function fetchEvents(): Promise<EventsResponse> {
  const response = await fetch(`${API_BASE_URL}/events`);
  if (!response.ok) throw new Error("events api failed");
  return response.json();
}
