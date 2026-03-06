export interface CodeDecoration {
  line: number;
  character?: number;
  endLine?: number;
  endCharacter?: number;
  kind: 'italic' | 'copilot';
}

export type CodeSampleLanguage = 'ts' | 'python' | 'rust' | 'go';

export interface CodeSample {
  label: string;
  value: string;
  lang: CodeSampleLanguage;
  code: string;
  decorations: CodeDecoration[];
}

export const codeSamples: CodeSample[] = [
  {
    label: 'TypeScript',
    value: 'typescript',
    lang: 'ts',
    code: `// Build a compact status summary
type User = {
  name: string;
  active: boolean;
  role: 'admin' | 'editor' | 'viewer';
};

const users: User[] = [
  { name: 'Alice', active: true, role: 'admin' },
  { name: 'Bob', active: false, role: 'viewer' },
];

// Copilot ghost text preview
const inlineSuggestion = users[0]?.name ?? 'No active users';

// Print the preview label
console.log(inlineSuggestion);`,
    decorations: [
      { line: 0, kind: 'italic' },
      { line: 12, kind: 'italic' },
      { line: 13, character: 43, endCharacter: -1, kind: 'copilot' },
      { line: 15, kind: 'italic' },
    ],
  },
  {
    label: 'Python',
    value: 'python',
    lang: 'python',
    code: `# Build a compact status summary
users = [
    {"name": "Alice", "active": True, "role": "admin"},
    {"name": "Bob", "active": False, "role": "viewer"},
]

active_names = [user["name"] for user in users if user["active"]]
active_count = len(active_names)

def format_status(count: int) -> str:
    return f"{count} active user{'s' if count != 1 else ''}"

preview_label = active_names[0] if active_names else "No active users"
status_line = format_status(active_count)

# Print the preview label
print(preview_label)
print(status_line)`,
    decorations: [
      { line: 0, kind: 'italic' },
      { line: 3, character: 36, endCharacter: -1, kind: 'copilot' },
      { line: 15, kind: 'italic' },
    ],
  },
  {
    label: 'Rust',
    value: 'rust',
    lang: 'rust',
    code: `// Build a compact status summary
let users = vec![
    ("Alice", true, "admin"),
    ("Bob", false, "viewer"),
];

let active_names: Vec<&str> = users
    .iter()
    .filter(|(_, active, _)| *active)
    .map(|(name, _, _)| *name)
    .collect();

// Copilot ghost text preview
let preview_label = active_names.first().copied().unwrap_or(
    "No active users",
);

// Print the preview label
println!("{preview_label}");`,
    decorations: [
      { line: 0, kind: 'italic' },
      { line: 12, kind: 'italic' },
      { line: 14, character: 4, endCharacter: -1, kind: 'copilot' },
      { line: 17, kind: 'italic' },
    ],
  },
  {
    label: 'Go',
    value: 'go',
    lang: 'go',
    code: `// Build a compact status summary
package main

import "fmt"

type User struct {
    Name   string
    Active bool
    Role   string
}

func main() {
    users := []User{
        {Name: "Alice", Active: true, Role: "admin"},
        {Name: "Bob", Active: false, Role: "viewer"},
    }

    label := "No active users"
    if users[0].Active {
        label = users[0].Name
    }

    // Print the preview label
    fmt.Println(label)
}`,
    decorations: [
      { line: 0, kind: 'italic' },
      { line: 19, character: 16, endCharacter: -1, kind: 'copilot' },
      { line: 22, kind: 'italic' },
    ],
  },
];
