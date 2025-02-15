export const endConversation = async (
    conversationId: string,
  ) => {
    try {
      const response = await fetch(
        `https://tavusapi.com/v2/conversations/${conversationId}/end`,
        {
          method: "POST",
          headers: {
            "x-api-key": "de1e8457a8404e15a25feff77c20ff6a",
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
  