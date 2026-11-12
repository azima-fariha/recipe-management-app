// Base URL for the consumer-api gateway (the same `*_URL` convention as the
// other services; see docker-compose.yml). Defaults to localhost for local,
// non-Docker development.
const CONSUMER_API_URL = process.env.CONSUMER_API_URL ?? "http://localhost:8088";

export interface ApiUser {
  id: number;
  full_name: string | null;
  email: string;
  dietary_restrictions?: string | null;
  preferences?: string | null;
  created_at?: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: ApiUser;
}

/** Thrown when consumer-api responds with a non-2xx status. */
export class ConsumerApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(status: number, body: unknown) {
    super(`consumer-api responded with ${status}`);
    this.name = "ConsumerApiError";
    this.status = status;
    this.body = body;
  }
}

async function parseJsonSafely(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const response = await fetch(`${CONSUMER_API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const body = await parseJsonSafely(response);
  if (!response.ok) {
    throw new ConsumerApiError(response.status, body);
  }
  return body as TokenResponse;
}

export interface SignupRequest {
  full_name: string;
  email: string;
  password: string;
}

export async function signup(data: SignupRequest): Promise<TokenResponse> {
  const response = await fetch(`${CONSUMER_API_URL}/user`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const body = await parseJsonSafely(response);
  if (!response.ok) {
    throw new ConsumerApiError(response.status, body);
  }
  return body as TokenResponse;
}

/**
 * Fetches a user's profile from consumer-api, forwarding the Access Token
 * as `Authorization: Bearer <token>` — the same mechanism any non-browser
 * API client would use. consumer-api never sees a cookie.
 */
export async function fetchUser(userId: string, token: string): Promise<ApiUser> {
  const response = await fetch(`${CONSUMER_API_URL}/user/${userId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  const body = await parseJsonSafely(response);
  if (!response.ok) {
    throw new ConsumerApiError(response.status, body);
  }
  return body as ApiUser;
}

export interface ApiRecipe {
  id: string;
  name: string;
  ingredients: string[];
  instructions: string;
}

export interface RecipeInput {
  name: string;
  ingredients: string[];
  instructions: string;
}

export interface RecipeUpdateInput {
  name?: string;
  ingredients?: string[];
  instructions?: string;
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

/** Lists the owning user's recipes. See GLOSSARY.md > Ownership. */
export async function fetchRecipes(userId: string, token: string): Promise<ApiRecipe[]> {
  const response = await fetch(`${CONSUMER_API_URL}/user/${userId}/recipe`, {
    headers: authHeaders(token),
  });

  const body = await parseJsonSafely(response);
  if (!response.ok) {
    throw new ConsumerApiError(response.status, body);
  }
  return body as ApiRecipe[];
}

/** Fetches a single recipe's full details. */
export async function fetchRecipeById(
  userId: string,
  recipeId: string,
  token: string,
): Promise<ApiRecipe> {
  const response = await fetch(`${CONSUMER_API_URL}/user/${userId}/recipe/${recipeId}`, {
    headers: authHeaders(token),
  });

  const body = await parseJsonSafely(response);
  if (!response.ok) {
    throw new ConsumerApiError(response.status, body);
  }
  return body as ApiRecipe;
}

export async function createRecipe(
  userId: string,
  token: string,
  data: RecipeInput,
): Promise<ApiRecipe> {
  const response = await fetch(`${CONSUMER_API_URL}/user/${userId}/recipe`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(data),
  });

  const body = await parseJsonSafely(response);
  if (!response.ok) {
    throw new ConsumerApiError(response.status, body);
  }
  return body as ApiRecipe;
}

export async function updateRecipe(
  userId: string,
  recipeId: string,
  token: string,
  data: RecipeUpdateInput,
): Promise<ApiRecipe> {
  const response = await fetch(`${CONSUMER_API_URL}/user/${userId}/recipe/${recipeId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(data),
  });

  const body = await parseJsonSafely(response);
  if (!response.ok) {
    throw new ConsumerApiError(response.status, body);
  }
  return body as ApiRecipe;
}

export async function deleteRecipe(userId: string, recipeId: string, token: string): Promise<void> {
  const response = await fetch(`${CONSUMER_API_URL}/user/${userId}/recipe/${recipeId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });

  if (!response.ok) {
    const body = await parseJsonSafely(response);
    throw new ConsumerApiError(response.status, body);
  }
}
