<!-- example.svelte — theme conflict testing: Svelte -->
<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from "svelte";
  import { writable, derived, get } from "svelte/store";
  import { fade, fly, slide } from "svelte/transition";
  import { cubicOut } from "svelte/easing";

  // ─── Props ────────────────────────────────────────────────────────────────

  export let userId: number;
  export let theme: "light" | "dark" = "dark";
  export let maxItems: number = 10;
  export let onSave: ((data: UserFormData) => void) | null = null;

  // ─── Types ────────────────────────────────────────────────────────────────

  interface User {
    id:       number;
    name:     string;
    email:    string;
    role:     "admin" | "editor" | "viewer";
    avatar:   string | null;
    settings: UserSettings;
  }

  interface UserSettings {
    notifications: boolean;
    darkMode:      boolean;
    language:      string;
  }

  interface UserFormData {
    name:  string;
    email: string;
    bio:   string;
  }

  interface Notification {
    id:      string;
    type:    "success" | "error" | "info";
    message: string;
  }

  // ─── Stores ───────────────────────────────────────────────────────────────

  const user       = writable<User | null>(null);
  const loading    = writable(true);
  const errors     = writable<Record<string, string>>({});
  const notifQueue = writable<Notification[]>([]);

  const isAdmin  = derived(user, $u => $u?.role === "admin");
  const fullName = derived(user, $u => $u?.name ?? "Anonymous");

  // ─── State ────────────────────────────────────────────────────────────────

  let form: UserFormData = { name: "", email: "", bio: "" };
  let showPanel = false;
  let activeTab = "profile";
  let items: string[] = [];
  let selectedIndex = -1;
  let inputRef: HTMLInputElement;

  // ─── Reactive declarations ────────────────────────────────────────────────

  $: isFormDirty = form.name !== ($user?.name ?? "") ||
                   form.email !== ($user?.email ?? "");

  $: truncatedItems = items.slice(0, maxItems);

  $: if ($user) {
    form = { name: $user.name, email: $user.email, bio: "" };
  }

  $: tabClass = (tab: string) =>
    `tab ${activeTab === tab ? "tab--active" : ""}`;

  // ─── Lifecycle ───────────────────────────────────────────────────────────

  const dispatch = createEventDispatcher<{
    save:   UserFormData;
    cancel: void;
    error:  { message: string };
  }>();

  let interval: ReturnType<typeof setInterval>;

  onMount(async () => {
    await fetchUser(userId);
    interval = setInterval(pollNotifications, 30_000);
    inputRef?.focus();
  });

  onDestroy(() => clearInterval(interval));

  // ─── Functions ────────────────────────────────────────────────────────────

  async function fetchUser(id: number) {
    loading.set(true);
    try {
      const res = await fetch(`/api/users/${id}`);
      user.set((await res.json()).data);
    } catch (e) {
      dispatch("error", { message: (e as Error).message });
    } finally {
      loading.set(false);
    }
  }

  async function pollNotifications() {
    const current = get(user);
    if (!current) return;
    const res = await fetch(`/api/users/${current.id}/notifications`);
    notifQueue.update(q => [...q, ...(await res.json()).data]);
  }

  function validate(): boolean {
    const errs: Record<string, string> = {};
    if (!form.name.trim()) errs.name = "Name is required";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = "Invalid email";
    errors.set(errs);
    return !Object.keys(errs).length;
  }

  function handleSubmit() {
    if (!validate()) return;
    onSave?.(form);
    dispatch("save", form);
    pushNotification("success", "Profile saved!");
  }

  function pushNotification(type: Notification["type"], message: string) {
    const id = crypto.randomUUID();
    notifQueue.update(q => [...q, { id, type, message }]);
    setTimeout(() => dismissNotification(id), 4_000);
  }

  function dismissNotification(id: string) {
    notifQueue.update(q => q.filter(n => n.id !== id));
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape")     { showPanel = false; return; }
    if (e.key === "ArrowDown")  selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
    if (e.key === "ArrowUp")    selectedIndex = Math.max(selectedIndex - 1, 0);
  }

  // property.property chains for theme testing ↓
  function describeUser(u: User): string {
    return `${u.name} — ${u.settings.language} — notifs ${u.settings.notifications ? "on" : "off"} — ${u.settings.darkMode ? "dark" : "light"} mode`;
  }
</script>

<!-- ─── Markup ──────────────────────────────────────────────────────────────── -->

<svelte:window on:keydown={handleKeydown} />

<div class="root" class:root--dark={theme === "dark"} data-testid="user-panel">

  <!-- Notification stack -->
  {#each $notifQueue as notif (notif.id)}
    <div
      class="notif notif--{notif.type}"
      transition:fly={{ y: -20, duration: 250, easing: cubicOut }}
      role="alert"
    >
      <span>{notif.message}</span>
      <button on:click={() => dismissNotification(notif.id)} aria-label="Dismiss">×</button>
    </div>
  {/each}

  <!-- Loading state -->
  {#if $loading}
    <div class="spinner" transition:fade={{ duration: 200 }}>
      <span class="sr-only">Loading…</span>
    </div>

  {:else if $user}
    <header class="header">
      <img
        src={$user.avatar ?? "/default-avatar.png"}
        alt="{$user.name}'s avatar"
        class="avatar"
      />
      <div class="header__meta">
        <h1>{$fullName}</h1>
        <p class="role">{$user.role}</p>
        {#if $isAdmin}
          <span class="badge badge--admin">Admin</span>
        {/if}
      </div>
      <button class="btn btn--icon" on:click={() => (showPanel = !showPanel)}>
        {showPanel ? "Close" : "Edit"}
      </button>
    </header>

    <!-- Tab bar -->
    <nav class="tabs" role="tablist">
      {#each ["profile", "settings", "activity"] as tab}
        <button
          role="tab"
          class={tabClass(tab)}
          aria-selected={activeTab === tab}
          on:click={() => (activeTab = tab)}
        >
          {tab}
        </button>
      {/each}
    </nav>

    <!-- Tab panels -->
    {#if activeTab === "profile"}
      <section transition:slide={{ duration: 200 }}>
        <p>{describeUser($user)}</p>

        {#if showPanel}
          <form on:submit|preventDefault={handleSubmit} class="form">
            <label class="field">
              <span>Name</span>
              <input
                bind:this={inputRef}
                bind:value={form.name}
                class:field__input--error={$errors.name}
                placeholder="Full name"
                autocomplete="name"
              />
              {#if $errors.name}
                <small class="field__error">{$errors.name}</small>
              {/if}
            </label>

            <label class="field">
              <span>Email</span>
              <input
                bind:value={form.email}
                type="email"
                class:field__input--error={$errors.email}
                placeholder="you@example.com"
                autocomplete="email"
              />
              {#if $errors.email}
                <small class="field__error">{$errors.email}</small>
              {/if}
            </label>

            <label class="field">
              <span>Bio</span>
              <textarea bind:value={form.bio} rows={4} placeholder="Tell us about yourself…" />
            </label>

            <div class="form__actions">
              <button type="submit" class="btn btn--primary" disabled={!isFormDirty}>Save</button>
              <button type="button" class="btn" on:click={() => dispatch("cancel")}>Cancel</button>
            </div>
          </form>
        {/if}
      </section>

    {:else if activeTab === "settings"}
      <section transition:slide={{ duration: 200 }}>
        <label class="toggle">
          <input type="checkbox" bind:checked={$user.settings.notifications} />
          <span>Email notifications</span>
        </label>
        <label class="toggle">
          <input type="checkbox" bind:checked={$user.settings.darkMode} />
          <span>Dark mode</span>
        </label>
        <select bind:value={$user.settings.language}>
          {#each ["en", "es", "fr", "de", "ja"] as lang}
            <option value={lang}>{lang.toUpperCase()}</option>
          {/each}
        </select>
      </section>

    {:else if activeTab === "activity"}
      <section transition:slide={{ duration: 200 }}>
        <ul class="item-list">
          {#each truncatedItems as item, i (i)}
            <li
              class="item"
              class:item--selected={selectedIndex === i}
              on:click={() => (selectedIndex = i)}
            >
              {item}
            </li>
          {:else}
            <li class="item item--empty">No activity yet.</li>
          {/each}
        </ul>
        {#if items.length > maxItems}
          <p class="hint">Showing {maxItems} of {items.length}</p>
        {/if}
      </section>
    {/if}

  {:else}
    <p class="empty-state">User not found.</p>
  {/if}
</div>

<!-- ─── Styles ──────────────────────────────────────────────────────────────── -->

<style>
  .root {
    --bg:      #1a2e1a;
    --surface: #243324;
    --text:    #c8e6c8;
    --accent:  #6abf6a;
    --error:   #e06c6c;
    font-family: "JetBrains Mono", monospace;
    background: var(--bg);
    color:      var(--text);
    padding:    1.5rem;
    border-radius: 8px;
  }
  .header       { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
  .avatar       { width: 48px; height: 48px; border-radius: 50%; }
  .tabs         { display: flex; gap: 0.5rem; border-bottom: 1px solid var(--surface); margin-bottom: 1rem; }
  .tab          { background: none; border: none; color: var(--text); padding: 0.4rem 0.8rem; cursor: pointer; }
  .tab--active  { color: var(--accent); border-bottom: 2px solid var(--accent); }
  .btn          { background: var(--surface); color: var(--text); border: 1px solid var(--accent); padding: 0.4rem 1rem; border-radius: 4px; cursor: pointer; }
  .btn--primary { background: var(--accent); color: var(--bg); }
  .field        { display: flex; flex-direction: column; gap: 0.25rem; margin-bottom: 0.75rem; }
  .field__error { color: var(--error); font-size: 0.75rem; }
  .notif        { position: fixed; top: 1rem; right: 1rem; padding: 0.6rem 1rem; border-radius: 4px; }
  .notif--success { background: #2d4a2d; border-left: 3px solid var(--accent); }
  .notif--error   { background: #4a2d2d; border-left: 3px solid var(--error); }
  .badge        { font-size: 0.65rem; padding: 0.1rem 0.4rem; border-radius: 3px; background: var(--accent); color: var(--bg); }
  .spinner      { width: 24px; height: 24px; border: 2px solid var(--accent); border-top-color: transparent; border-radius: 50%; animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
