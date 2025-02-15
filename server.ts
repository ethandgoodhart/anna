import { Hono } from "hono";
import { createCloudflareContext, setupRemixHandler } from "~/utils/handlers";

const app = new Hono<{ Bindings: Env }>();

app.get("/hello", (c) => {
	return c.text("Hello World");
});

app.all("*", async (c) => {
	try {
		const handleRemixRequest = setupRemixHandler();
		const loadContext = createCloudflareContext(
			c.req.raw,
			c.env,
			c.executionCtx as ExecutionContext,
		);
		const response = await handleRemixRequest(c.req.raw, loadContext);

		return response;
	} catch (error) {
		console.error(error);
		return new Response("An unexpected error occurred", { status: 500 });
	}
});

export default app;
