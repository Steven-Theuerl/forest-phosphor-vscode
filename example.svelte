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

  const user             = writable<User | null>(null);
  const loading          = writable(true);
  const formErrors       = writable<Record<string, string>>({});
  const notifQueue       = writable<Notification[]>([]);

  const isAdmin = derived(user, (currentUser) => {
    if (currentUser === null) return false;
    return currentUser.role === "admin";
  });

  const fullName = derived(user, (currentUser) => {
    if (currentUser === null) return "Anonymous";
    return currentUser.name;
  });

  // ─── State ────────────────────────────────────────────────────────────────

  let form: UserFormData = { name: "", email: "", bio: "" };
  let showPanel = false;
  let activeTab = "profile";
  let items: string[] = [];
  let selectedIndex = -1;
  let inputRef: HTMLInputElement;

  // Local copies of settings used for two-way binding
  let notificationsEnabled = false;
  let darkModeEnabled = false;
  let selectedLanguage = "en";

  // ─── Reactive declarations ────────────────────────────────────────────────

  let isFormDirty = false;
  $: {
    const savedName  = $user !== null ? $user.name  : "";
    const savedEmail = $user !== null ? $user.email : "";
    isFormDirty = form.name !== savedName || form.email !== savedEmail;
  }

  $: truncatedItems = items.slice(0, maxItems);

  $: if ($user) {
    form                  = { name: $user.name, email: $user.email, bio: "" };
    notificationsEnabled  = $user.settings.notifications;
    darkModeEnabled       = $user.settings.darkMode;
    selectedLanguage      = $user.settings.language;
  }

  function getTabClass(tabName: string): string {
    if (activeTab === tabName) {
      return "tab tab--active";
    }
    return "tab";
  }

  // ─── Lifecycle ───────────────────────────────────────────────────────────

  const dispatch = createEventDispatcher<{
    save:   UserFormData;
    cancel: void;
    error:  { message: string };
  }>();

  let pollingInterval: ReturnType<typeof setInterval>;

  onMount(async () => {
    await fetchUser(userId);
    pollingInterval = setInterval(pollNotifications, 30_000);
    if (inputRef) {
      inputRef.focus();
    }
  });

  onDestroy(() => clearInterval(pollingInterval));

  // ─── Functions ────────────────────────────────────────────────────────────

  async function fetchUser(id: number) {
    loading.set(true);
    try {
      const response     = await fetch(`/api/users/${id}`);
      const responseData = await response.json();
      user.set(responseData.data);
    } catch (fetchError) {
      dispatch("error", { message: (fetchError as Error).message });
    } finally {
      loading.set(false);
    }
  }

  async function pollNotifications() {
    const currentUser = get(user);
    if (currentUser === null) return;

    const response          = await fetch(`/api/users/${currentUser.id}/notifications`);
    const responseData      = await response.json();
    const newNotifications: Notification[] = responseData.data;

    notifQueue.update(currentQueue => [...currentQueue, ...newNotifications]);
  }

  function validate(): boolean {
    const validationErrors: Record<string, string> = {};

    if (!form.name.trim()) {
      validationErrors.name = "Name is required";
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(form.email)) {
      validationErrors.email = "Invalid email";
    }

    formErrors.set(validationErrors);
    return Object.keys(validationErrors).length === 0;
  }

  function handleSubmit() {
    if (!validate()) return;

    if (onSave !== null) {
      onSave(form);
    }

    dispatch("save", form);
    pushNotification("success", "Profile saved!");
  }

  function pushNotification(notifType: Notification["type"], message: string) {
    const notificationId = crypto.randomUUID();
    const newNotification: Notification = { id: notificationId, type: notifType, message };

    notifQueue.update(currentQueue => [...currentQueue, newNotification]);
    setTimeout(() => dismissNotification(notificationId), 4_000);
  }

  function dismissNotification(notificationId: string) {
    notifQueue.update(currentQueue =>
      currentQueue.filter(notification => notification.id !== notificationId)
    );
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape") {
      showPanel = false;
      return;
    }
    if (event.key === "ArrowDown") {
      selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
    }
    if (event.key === "ArrowUp") {
      selectedIndex = Math.max(selectedIndex - 1, 0);
    }
  }

  function handleSettingsChange() {
    user.update(currentUser => {
      if (currentUser === null) return null;
      return {
        ...currentUser,
        settings: {
          notifications: notificationsEnabled,
          darkMode:      darkModeEnabled,
          language:      selectedLanguage,
        },
      };
    });
  }

  // property.property chains for theme testing ↓
  function describeUser(targetUser: User): string {
    const notificationStatus = targetUser.settings.notifications ? "on" : "off";
    const colorMode          = targetUser.settings.darkMode ? "dark" : "light";
    return `${targetUser.name} — ${targetUser.settings.language} — notifs ${notificationStatus} — ${colorMode} mode`;
  }
</script>

<!-- ─── Markup ──────────────────────────────────────────────────────────────── -->

<svelte:window on:keydown={handleKeydown} />

<div class="root" class:root--dark={theme === "dark"} data-testid="user-panel">

  <!-- Notification stack -->
  {#each $notifQueue as notification (notification.id)}
    <div
      class="notif notif--{notification.type}"
      transition:fly={{ y: -20, duration: 250, easing: cubicOut }}
      role="alert"
    >
      <span>{notification.message}</span>
      <button on:click={() => dismissNotification(notification.id)} aria-label="Dismiss">×</button>
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
        src={$user.avatar !== null ? $user.avatar : "/default-avatar.png"}
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
      <button class="btn btn--icon" on:click={() => { showPanel = !showPanel; }}>
        {showPanel ? "Close" : "Edit"}
      </button>
    </header>

    <!-- Tab bar -->
    <nav class="tabs" role="tablist">
      {#each ["profile", "settings", "activity"] as tabName}
        <button
          role="tab"
          class={getTabClass(tabName)}
          aria-selected={activeTab === tabName}
          on:click={() => { activeTab = tabName; }}
        >
          {tabName}
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
                class:field__input--error={$formErrors.name}
                placeholder="Full name"
                autocomplete="name"
              />
              {#if $formErrors.name}
                <small class="field__error">{$formErrors.name}</small>
              {/if}
            </label>

            <label class="field">
              <span>Email</span>
              <input
                bind:value={form.email}
                type="email"
                class:field__input--error={$formErrors.email}
                placeholder="you@example.com"
                autocomplete="email"
              />
              {#if $formErrors.email}
                <small class="field__error">{$formErrors.email}</small>
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
          <input
            type="checkbox"
            bind:checked={notificationsEnabled}
            on:change={handleSettingsChange}
          />
          <span>Email notifications</span>
        </label>
        <label class="toggle">
          <input
            type="checkbox"
            bind:checked={darkModeEnabled}
            on:change={handleSettingsChange}
          />
          <span>Dark mode</span>
        </label>
        <select bind:value={selectedLanguage} on:change={handleSettingsChange}>
          {#each ["en", "es", "fr", "de", "ja"] as languageCode}
            <option value={languageCode}>{languageCode.toUpperCase()}</option>
          {/each}
        </select>
      </section>

    {:else if activeTab === "activity"}
      <section transition:slide={{ duration: 200 }}>
        <ul class="item-list">
          {#each truncatedItems as item, itemIndex (itemIndex)}
            <li
              class="item"
              class:item--selected={selectedIndex === itemIndex}
              on:click={() => { selectedIndex = itemIndex; }}
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
