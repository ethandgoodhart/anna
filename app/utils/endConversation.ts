export const endConversation = async (
    conversationId: string,
  ) => {
    try {
      const response = await fetch(
        `https://tavusapi.com/v2/conversations/${conversationId}/end`,
        {
          method: "POST",
          headers: {
            "x-api-key": "a335c04a5be24585af0ddae7e08c40e5",
          },
        },
      );
  
      if (!response.ok) {
        throw new Error("Failed to end conversation");
      }
  
      return null;
    } catch (error) {
      console.error("Error:", error);
      throw error;
    }
  };
  