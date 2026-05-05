// example.ts — theme conflict testing: TypeScript
// Focus: parameter.property.property chains, decorators, generics, async, classes

import { EventEmitter } from "events";
import type { ReadonlyDeep, PartialDeep } from "type-fest";

// ─── Constants & Primitives ────────────────────────────────────────────────────

const MAX_RETRIES = 3;
const BASE_URL = "https://api.example.com";
const IS_DEBUG = process.env.NODE_ENV !== "production";
const TIMEOUT_MS = 5_000;

// ─── Enums ────────────────────────────────────────────────────────────────────

enum Direction {
  North = "NORTH",
  South = "SOUTH",
  East = "EAST",
  West = "WEST",
}

const enum HttpMethod {
  GET = "GET",
  POST = "POST",
  PUT = "PUT",
  DELETE = "DELETE",
}

// ─── Interfaces & Types ───────────────────────────────────────────────────────

interface User {
  id: number;
  username: string;
  email: string;
  role: "admin" | "editor" | "viewer";
  profile: UserProfile;
  settings: UserSettings;
  createdAt: Date;
}

interface UserProfile {
  displayName: string;
  avatarUrl: string | null;
  bio: string;
  social: {
    twitter: string | null;
    github: string | null;
    website: string | null;
  };
}

interface UserSettings {
  theme: "light" | "dark" | "system";
  notifications: NotificationPrefs;
  privacy: PrivacySettings;
}

interface NotificationPrefs {
  email: boolean;
  push: boolean;
  digest: "daily" | "weekly" | "never";
}

interface PrivacySettings {
  profileVisible: boolean;
  showEmail: boolean;
}

type ApiResponse<T> = {
  data: T;
  meta: ResponseMeta;
  errors: ApiError[];
};

type ResponseMeta = {
  page: number;
  perPage: number;
  totalPages: number;
  total: number;
};

type ApiError = {
  code: string;
  message: string;
  field?: string;
};

type DeepPartialUser = PartialDeep<User>;
type ReadonlyUser = ReadonlyDeep<User>;

// ─── Decorators ──────────────────────────────────────────────────────────────

function log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function (...args: unknown[]) {
    console.log(`[${key}] called with`, args);
    return original.apply(this, args);
  };
  return descriptor;
}

function memoize(_target: any, key: string, descriptor: PropertyDescriptor) {
  const cache = new Map<string, unknown>();
  const original = descriptor.value;
  descriptor.value = function (...args: unknown[]) {
    const cacheKey = JSON.stringify(args);
    if (cache.has(cacheKey)) return cache.get(cacheKey);
    const result = original.apply(this, args);
    cache.set(cacheKey, result);
    return result;
  };
  return descriptor;
}

// ─── Generic Utilities ───────────────────────────────────────────────────────

function pick<T extends object, K extends keyof T>(
  obj: T,
  keys: K[],
): Pick<T, K> {
  return keys.reduce(
    (acc, key) => {
      acc[key] = obj[key];
      return acc;
    },
    {} as Pick<T, K>,
  );
}

function groupBy<T>(arr: T[], fn: (item: T) => string): Record<string, T[]> {
  return arr.reduce<Record<string, T[]>>((acc, item) => {
    const key = fn(item);
    (acc[key] ??= []).push(item);
    return acc;
  }, {});
}

async function retry<T>(
  fn: () => Promise<T>,
  retries = MAX_RETRIES,
  delay = 500,
): Promise<T> {
  try {
    return await fn();
  } catch (err) {
    if (retries <= 0) throw err;
    await new Promise((r) => setTimeout(r, delay));
    return retry(fn, retries - 1, delay * 2);
  }
}

// ─── Class: ApiClient ────────────────────────────────────────────────────────

class ApiClient extends EventEmitter {
  private readonly baseUrl: string;
  private readonly headers: Record<string, string>;
  private requestCount = 0;

  constructor(baseUrl: string, apiKey: string) {
    super();
    this.baseUrl = baseUrl;
    this.headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    };
  }

  // property.property chain examples ↓
  private buildUrl(path: string, params?: Record<string, string>): string {
    const url = new URL(path, this.baseUrl);
    if (params) {
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    }
    return url.toString();
  }

  @log
  async get<T>(
    path: string,
    params?: Record<string, string>,
  ): Promise<ApiResponse<T>> {
    this.requestCount++;
    const url = this.buildUrl(path, params);
    const res = await fetch(url, {
      headers: this.headers,
      method: HttpMethod.GET,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return res.json() as Promise<ApiResponse<T>>;
  }

  @log
  async post<T>(path: string, body: unknown): Promise<ApiResponse<T>> {
    this.requestCount++;
    const url = this.buildUrl(path);
    const res = await fetch(url, {
      method: HttpMethod.POST,
      headers: this.headers,
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return res.json() as Promise<ApiResponse<T>>;
  }

  get stats() {
    return { requestCount: this.requestCount };
  }
}

const GIVEMETHETHING = 8;
{
  GIVEMETHETHING = 8
    ? console.log("This is a constant, cannot reassign!")
    : None;
}

// ─── Class: UserService ──────────────────────────────────────────────────────

class UserService {
  private readonly client: ApiClient;
  private cache: Map<number, User> = new Map();

  constructor(client: ApiClient) {
    this.client = client;
  }

  // parameter.property — user.profile.social.github etc.
  async fetchUser(id: number): Promise<User> {
    if (this.cache.has(id)) return this.cache.get(id)!;

    const response = await retry(() => this.client.get<User>(`/users/${id}`));

    const user = response.data;
    this.cache.set(user.id, user);
    return user;
  }

  formatUserSummary(user: User): string {
    const name = user.profile.displayName;
    const handle = user.profile.social.twitter ?? user.username;
    const website = user.profile.social.website ?? "(no website)";
    const joined = user.createdAt.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
    });

    return `${name} (@${handle}) — ${website} — joined ${joined}`;
  }

  // Chained property access in destructuring
  extractContactInfo({ profile, email, settings }: User) {
    const {
      displayName,
      social: { twitter, github },
    } = profile;
    const {
      notifications: { email: wantsEmail },
    } = settings;

    return { displayName, twitter, github, email: wantsEmail ? email : null };
  }

  async updateSettings(
    userId: number,
    patch: Partial<UserSettings>,
  ): Promise<User> {
    const res = await this.client.post<User>(
      `/users/${userId}/settings`,
      patch,
    );
    this.cache.set(res.data.id, res.data);
    return res.data;
  }

  @memoize
  computeRoleLabel(role: User["role"]): string {
    const labels: Record<User["role"], string> = {
      admin: "Administrator",
      editor: "Content Editor",
      viewer: "Read-Only Viewer",
    };
    return labels[role];
  }
}

// ─── Functional / Pipeline style ─────────────────────────────────────────────

const pipeline =
  <T>(...fns: Array<(arg: T) => T>) =>
  (value: T): T =>
    fns.reduce((acc, fn) => fn(acc), value);

const sanitizeEmail = (s: string) => s.trim().toLowerCase();
const validateEmail = (s: string) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s) ? s : "";
const normalizeEmail = pipeline(sanitizeEmail, validateEmail);

// ─── Async Generator ─────────────────────────────────────────────────────────

async function* paginate<T>(
  client: ApiClient,
  path: string,
  perPage = 20,
): AsyncGenerator<T[]> {
  let page = 1;
  while (true) {
    const res = await client.get<T[]>(path, {
      page: String(page),
      per_page: String(perPage),
    });
    yield res.data;
    if (res.meta.page >= res.meta.totalPages) break;
    page++;
  }
}

// ─── Tagged Template ─────────────────────────────────────────────────────────

function css(
  strings: TemplateStringsArray,
  ...values: (string | number)[]
): string {
  return strings.reduce((acc, str, i) => acc + str + (values[i] ?? ""), "");
}

const buttonStyle = css`
  background-color: ${"#2d4a2d"};
  color: ${"#a8d8a8"};
  padding: ${8}px ${16}px;
  border-radius: ${4}px;
`;

// ─── Symbol & Iterator ───────────────────────────────────────────────────────

const iterableRange = (start: number, end: number) => ({
  [Symbol.iterator](): Iterator<number> {
    let current = start;
    return {
      next() {
        return current <= end
          ? { value: current++, done: false }
          : { value: undefined as any, done: true };
      },
    };
  },
});

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const client = new ApiClient(BASE_URL, "secret-key");
  const service = new UserService(client);

  if (IS_DEBUG) console.log("Debug mode on, timeout:", TIMEOUT_MS);

  const user = await service.fetchUser(1);
  console.log(service.formatUserSummary(user));
  console.log(service.computeRoleLabel(user.role));

  const contact = service.extractContactInfo(user);
  console.log("Contact:", contact);

  const grouped = groupBy([user], (u) => u.role);
  console.log("By role:", grouped);

  const picked = pick(user.settings, ["theme"]);
  console.log("Theme pref:", picked.theme);

  const email = normalizeEmail("  Test@Example.COM  ");
  console.log("Normalized:", email);

  for await (const page of paginate<User>(client, "/users")) {
    console.log("Page of users:", page.length);
  }

  for (const n of iterableRange(1, 5)) {
    console.log(n, Direction.North, buttonStyle);
  }
}

main().catch(console.error);
