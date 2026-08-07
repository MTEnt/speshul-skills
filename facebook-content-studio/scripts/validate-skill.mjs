#!/usr/bin/env node

import { access, readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const requiredFiles = [
  'SKILL.md',
  'references/content-strategy.md',
  'references/continuity-system.md',
  'references/higgsfield-routing.md',
  'references/meta-publishing.md',
  'templates/creative-interview.md',
  'templates/campaign-brief.md',
  'templates/continuity-bible.md',
  'templates/asset-registry.schema.md',
  'templates/shot-list.md',
  'templates/post-package.schema.md',
  'brand-profiles/workshop-ai.yaml',
  'examples/post-package.example.json',
  'scripts/validate-post-package.mjs',
];

const errors = [];
for (const relativePath of requiredFiles) {
  try {
    await access(resolve(skillRoot, relativePath));
  } catch {
    errors.push(`Missing required file: ${relativePath}`);
  }
}

const skillText = await readFile(resolve(skillRoot, 'SKILL.md'), 'utf8');
if (!skillText.startsWith('---\n')) errors.push('SKILL.md must start with YAML frontmatter');
if (!/^name: facebook-content-studio$/m.test(skillText)) errors.push('SKILL.md frontmatter has the wrong name');
if (!/^version: 0\.1\.0$/m.test(skillText)) errors.push('SKILL.md frontmatter has the wrong version');
if (!/^description: \|$/m.test(skillText)) errors.push('SKILL.md needs a multiline description');

for (const downstream of [
  'higgsfield-generate',
  'higgsfield-soul-id',
  'higgsfield-product-photoshoot',
  'higgsfield-video-explainer',
  'facebook_post_preview',
  'facebook_post_publish',
]) {
  if (!skillText.includes(downstream)) errors.push(`SKILL.md does not name required capability: ${downstream}`);
}

const workshopProfile = await readFile(resolve(skillRoot, 'brand-profiles/workshop-ai.yaml'), 'utf8');
if (!/^status: needs_interview$/m.test(workshopProfile)) {
  errors.push('Workshop AI profile must remain needs_interview until brand details are supplied');
}

if (errors.length > 0) {
  for (const error of errors) console.error(`Error: ${error}`);
  process.exitCode = 1;
} else {
  console.log(`Valid skill package: ${skillRoot}`);
}
