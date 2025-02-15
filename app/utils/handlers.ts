import { type ServerBuild, createRequestHandler } from "@remix-run/cloudflare";
import * as build from "../../build/server"; 
import { getLoadContext } from "../../load-context";

// Abstract Remix handler setup
export const setupRemixHandler = () => {
	return createRequestHandler(build as unknown as ServerBuild);
};

// Create context for Remix from Cloudflare env
export const createCloudflareContext = (
	request: Request,
	env: Env,
	ctx: ExecutionContext,
) => {
	return getLoadContext({
		request,
		context: {
			cloudflare: {
				cf: request.cf,
				ctx: {
					waitUntil: ctx.waitUntil.bind(ctx),
					passThroughOnException: ctx.passThroughOnException.bind(ctx),
				},
				caches,
				env,
			},
		},
	});
};
