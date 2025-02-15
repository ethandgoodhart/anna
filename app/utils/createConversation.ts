import type { IConversation } from "../types";

export const createConversation = async (): Promise<IConversation> => {
  const response = await fetch("https://tavusapi.com/v2/conversations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": "a335c04a5be24585af0ddae7e08c40e5",
    },
    body: JSON.stringify({
      persona_id: "p9a95912",
      properties: {
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
