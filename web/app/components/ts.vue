<template>
  <div
    class="font-preview"
    :style="{
      '--regular': regularFont,
      '--italic': italicFont,
      '--copilot': copilotFont,
    }"
  >
    <Shiki
      lang="ts"
      :code="code"
      class=""
      :highlight-options="{
        theme: 'github-dark-default',
        decorations: [
          {
            start: { line: 0, character: 0 },
            end: { line: 0, character: -1 },
            properties: { style: 'font-family: var(--italic); font-style: italic;' },
          },
          {
            start: { line: 8, character: 14 },
            end: { line: 8, character: -1 },
            properties: { style: 'font-family: var(--copilot);', class: 'copilot-line' },
          },
          {
            start: { line: 10, character: 0 },
            end: { line: 10, character: -1 },
            properties: { style: 'font-family: var(--italic); font-style: italic;' },
          },
          {
            start: { line: 18, character: 0 },
            end: { line: 18, character: -1 },
            properties: { style: 'font-family: var(--italic); font-style: italic;' },
          },
          {
            start: { line: 23, character: 0 },
            end: { line: 23, character: -1 },
            properties: { style: 'font-family: var(--italic); font-style: italic;' },
          },
          {
            start: { line: 45, character: 0 },
            end: { line: 45, character: -1 },
            properties: { style: 'font-family: var(--italic); font-style: italic;' },
          },
          {
            start: { line: 51, character: 0 },
            end: { line: 51, character: -1 },
            properties: { style: 'font-family: var(--italic); font-style: italic;' },
          },
        ],
      }"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  regularFont: string;
  italicFont: string;
  copilotFont: string;
}>();

const code = ref(`// Type definition for a user record
type User = {
  id: number;
  name: string;
  role: "admin" | "editor" | "viewer";
  active: boolean;
};

const query = "Copilot inline complete";
const suggestion = query + " demo";

// Sample data used in the demo
const users: User[] = [
  { id: 1, name: "Alice", role: "admin", active: true },
  { id: 2, name: "Bob", role: "editor", active: true },
  { id: 3, name: "Charlie", role: "viewer", active: false },
  { id: 4, name: "Dana", role: "editor", active: true },
];

// Utility function to pad text so table columns align
function pad(text: string, width: number): string {
  return text.padEnd(width, " ");
}

// Function that prints a simple aligned user table
function printUserTable(list: User[]): void {
  const header =
    pad("ID", 4) +
    pad("NAME", 12) +
    pad("ROLE", 10) +
    "ACTIVE";

  console.log(header);
  console.log("-".repeat(header.length));

  for (const u of list) {
    const row =
      pad(String(u.id), 4) +
      pad(u.name, 12) +
      pad(u.role, 10) +
      String(u.active);

    console.log(row);
  }
}

// Program entry point
function main(): void {
  console.log("User Table");
  printUserTable(users);
}

// Run the program
main();`);
</script>

<style lang="css">
.shiki {
  background-color: transparent !important;
}

.font-preview pre,
.font-preview code,
.font-preview .line {
  font-family: var(--regular), monospace;
}

.copilot-line {
  border-left: white 2px solid;
}

.copilot-line > span {
  color: #8b949e !important;
  opacity: 0.5;
}
</style>
