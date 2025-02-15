import type { IConversation } from "../types";

export const createConversation = async (): Promise<IConversation> => {
  const response = await fetch("https://tavusapi.com/v2/conversations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": "de1e8457a8404e15a25feff77c20ff6a",
    },
    body: JSON.stringify({
      // Stock Demo Persona
      persona_id: "p9a95912",
      properties: {
        // Apply greenscreen to the background
        apply_greenscreen: true,
      },
    }),
  });

  if (!response?.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data as IConversation;
};
