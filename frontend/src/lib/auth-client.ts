import { createAuthClient } from "better-auth/react";

// The Better Auth handler lives in this Next.js application. Using the current
// origin avoids accidentally sending authentication requests to the Python API.
export const authClient = createAuthClient();

export type AuthClient = typeof authClient;
