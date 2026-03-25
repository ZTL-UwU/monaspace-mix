<template>
  <div class="opacity-0 select-none h-0" aria-hidden="true">
    <span v-for="font in fontItems" :key="font" :style="{ fontFamily: fontFamily[font] }">
      {{ font }}
    </span>
  </div>

  <UContainer>
    <UPageHero :links="links">
      <template #title>
        <span class="glow" data-text="Monaspace ">Monaspace</span>
        <span>&nbsp;</span>
        <span class="glow font-neon text-(--color-neon)" data-text="M">M</span>
        <span class="glow font-radon text-(--color-radon)" data-text="i">i</span>
        <span class="glow font-xenon text-(--color-xenon)" data-text="x">x</span>
      </template>
    </UPageHero>
    <div class="grid md:grid-cols-6 gap-4 md:gap-10">
      <UCard
        class="md:col-span-4"
        :ui="{
          header: 'p-0!',
          body: 'p-0! bg-zinc-950/30',
        }"
      >
        <template #header>
          <UTabs
            v-model="selectedLanguage"
            color="neutral"
            variant="link"
            :content="false"
            :items="tabItems"
            class="w-full"
          />
        </template>
        <div class="max-h-107 overflow-y-auto px-8 py-4">
          <CodePreview
            :regular-font="regularFontFamily"
            :italic-font="italicFontFamily"
            :copilot-font="copilotFontFamily"
            :italic-from-upright="italicFromUpright"
            :sample="currentSample"
          />
        </div>
      </UCard>
      <UCard class="md:col-span-2" :ui="{ body: 'p-0!' }">
        <div class="border-b border-default p-5">
          <span class="text-2xl block mb-2" :class="[fontStyle[regularFont]]">Regular</span>
          <USelect v-model="regularFont" :items="fontItems" variant="soft" size="lg" class="w-full" />
        </div>
        <div class="border-b border-default p-5">
          <span class="text-2xl block mb-2" :class="[fontStyle[italicFont], { italic: !italicFromUpright }]">Italic</span>
          <USelect v-model="italicFont" :items="fontItems" variant="soft" size="lg" class="w-full" />
        </div>
        <UCheckbox v-model="italicFromUpright" label="Use upright as italic" class="border-b border-default p-5 truncate" />
        <div class="border-b border-default p-5">
          <span class="text-2xl block mb-2" :class="[fontStyle[copilotFont]]">Copilot</span>
          <USelect v-model="copilotFont" :items="fontItems" variant="soft" size="lg" class="w-full" />
        </div>
        <UCheckbox v-model="useNF" label="Use Nerd Fonts" class="p-5" />
      </UCard>
    </div>
    <div class="grid md:grid-cols-6 mt-4 md:mt-10 gap-4 md:gap-0 mb:24 sm:mb-32 lg:mb-40">
      <UPageCard
        variant="subtle"
        icon="tabler:circle-number-1"
        title="Download Fonts"
        :ui="{
          leading: 'text-2xl',
          title: 'font-bold text-xl uppercase',
        }"
        class="md:rounded-none first:rounded-l-lg last:rounded-r-lg md:col-span-2"
      >
        <div>
          <UButton icon="lucide:download" size="xl" variant="soft" class="w-full" :to="downloadLink" target="_blank">
            Download
          </UButton>
          <div class="flex items-center gap-2 mt-4 px-3 text-muted text-xs">
            <UIcon name="lucide:file" size="12" />
            {{ fileName }}
          </div>
        </div>
      </UPageCard>
      <UPageCard
        variant="subtle"
        icon="tabler:circle-number-2"
        title="VScode Settings"
        :ui="{
          leading: 'text-2xl',
          title: 'font-bold text-xl uppercase',
        }"
        class="md:rounded-none first:rounded-l-lg last:rounded-r-lg md:col-span-4 overflow-x-scroll"
      >
        <UCard class="relative">
          <UButton icon="lucide:clipboard" class="absolute right-6" variant="subtle" size="xl" @click="handleClick" />
          <Shiki lang="json" :code="vscodeSettingCode" />
        </UCard>
      </UPageCard>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
import type { ButtonProps, TabsItem } from '@nuxt/ui';
import { codeSamples } from '~/utils/codeSamples';

useSeoMeta({
  title: 'Monaspace Mix',
  description: 'Monaspace Mix is a collection of patched Monaspace fonts that you can mix and match to create your own unique coding font.',
});

definePageMeta({
  colorMode: 'dark',
});

const tabItems: TabsItem[] = codeSamples.map(sample => ({
  label: sample.label,
  value: sample.value,
}));

const links = ref<ButtonProps[]>([
  {
    label: 'GitHub',
    to: 'https://github.com/ZTL-UwU/monaspace-mix',
    icon: 'lucide:github',
    variant: 'ghost',
  },
  {
    label: 'Sponsor',
    to: 'https://ko-fi.com/ztl_uwu',
    icon: 'lucide:heart',
    variant: 'ghost',
  },
]);

const fontItems = ref(['Neon', 'Argon', 'Xenon', 'Radon', 'Krypton']);
const fontStyle: { [key: string]: string } = {
  Neon: 'font-neon text-(--color-neon)',
  Argon: 'font-argon text-(--color-argon)',
  Xenon: 'font-xenon text-(--color-xenon)',
  Radon: 'font-radon text-(--color-radon)',
  Krypton: 'font-krypton text-(--color-krypton)',
};

const fontFamily: { [key: string]: string } = {
  Neon: 'Monaspace Neon',
  Argon: 'Monaspace Argon',
  Xenon: 'Monaspace Xenon',
  Radon: 'Monaspace Radon',
  Krypton: 'Monaspace Krypton',
};

const regularFont = ref('Neon');
const italicFont = ref('Radon');
const copilotFont = ref('Krypton');
const selectedLanguage = ref(codeSamples[0]?.value ?? 'typescript');
const italicFromUpright = ref(false);
const useNF = ref(false);

const regularFontFamily = computed(() => fontFamily[regularFont.value] ?? 'Monaspace Neon');
const italicFontFamily = computed(() => fontFamily[italicFont.value] ?? 'Monaspace Radon');
const copilotFontFamily = computed(() => fontFamily[copilotFont.value] ?? 'Monaspace Krypton');

const currentSample = computed(() => {
  return codeSamples.find(sample => sample.value === selectedLanguage.value) ?? codeSamples[0]!;
});

const mixedFontName = computed(() => {
  return `Monaspace Mix ${regularFont.value}-${italicFont.value}${italicFromUpright.value ? ' UprightItalic' : ''}${useNF.value ? ' NF' : ''}`;
});

const fileName = computed(() => {
  return `Monaspace-Mix-${regularFont.value}-${italicFont.value}${italicFromUpright.value ? '-UprightItalic' : ''}${useNF.value ? '-NF' : ''}.zip`;
});

const vscodeSettingCode = computed(() => {
  return `{
  "editor.fontFamily": "${mixedFontName.value}",
  "editor.inlineSuggest.fontFamily": "${fontFamily[copilotFont.value]}",
}`;
});

const { copy } = useClipboard({ source: vscodeSettingCode, legacy: true });
const copied = ref(false);
const toast = useToast();
const shikiDirectivePattern = /\s*\/\/\s*\[!code (focus|\+\+|--|error|warning)\]/g;

async function handleClick() {
  await copy(vscodeSettingCode.value.replaceAll(shikiDirectivePattern, ''));
  copied.value = true;

  toast.add({
    title: 'Copied to clipboard',
    icon: 'lucide:clipboard',
  });
}

const checkIconRef = useTemplateRef('checkIconRef');
onClickOutside(checkIconRef, () => {
  copied.value = false;
});

const downloadLink = computed(() => {
  return `https://github.com/ZTL-UwU/monaspace-mix/releases/latest/download/${fileName.value}`;
});
</script>

<style lang="css">
.shiki {
  background-color: transparent !important;
}

.glow {
  position: relative;
}

.glow::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  color: currentColor;
  opacity: 60%;
  filter: blur(6px);
  pointer-events: none;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  -moz-backface-visibility: hidden;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  -moz-transform: translateZ(0);
}

code {
  counter-reset: step;
  counter-increment: step 0;
}

code .line::before {
  content: counter(step);
  counter-increment: step;
  width: 1rem;
  margin-right: 1.5rem;
  display: inline-block;
  text-align: right;
  color: #8b949e;
  font-family: 'Monaspace Neon', monospace;
  font-style: normal;
}
</style>
