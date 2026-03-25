<template>
  <UApp>
    <UMain>
      <NuxtPage />
    </UMain>

    <UFooter>
      <template #left>
        <p class="text-muted text-sm">
          Copyright © {{ new Date().getFullYear() }}
        </p>
      </template>
      <template #right>
        <UButton
          icon="lucide:github"
          color="neutral"
          variant="ghost"
          size="lg"
          to="https://github.com/ZTL-UwU/monaspace-mix"
          target="_blank"
          aria-label="GitHub"
        />
      </template>
    </UFooter>
  </UApp>
</template>
