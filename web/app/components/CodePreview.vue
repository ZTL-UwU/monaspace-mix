<template>
  <div
    class="font-preview"
    :style="{
      '--regular': regularFont,
      '--italic': italicFont,
      '--italic-style': italicFromUpright ? 'normal' : 'italic',
      '--copilot': copilotFont,
    }"
  >
    <Shiki
      :key="sample.code"
      :lang="sample.lang"
      :code="sample.code"
      :highlight-options="highlightOptions"
    />
  </div>
</template>

<script setup lang="ts">
import type { CodeSample } from '~/utils/codeSamples';

const props = defineProps<{
  regularFont: string;
  italicFont: string;
  copilotFont: string;
  italicFromUpright: boolean;
  sample: CodeSample;
}>();

const highlightOptions = computed(() => ({
  theme: 'github-dark-default',
  decorations: props.sample.decorations.map(decoration => ({
    start: {
      line: decoration.line,
      character: decoration.character ?? 0,
    },
    end: {
      line: decoration.endLine ?? decoration.line,
      character: decoration.endCharacter ?? -1,
    },
    properties: decoration.kind === 'copilot'
      ? { style: 'font-family: var(--copilot);', class: 'copilot-line' }
      : { style: 'font-family: var(--italic); font-style: var(--italic-style);' },
  })),
}));
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
