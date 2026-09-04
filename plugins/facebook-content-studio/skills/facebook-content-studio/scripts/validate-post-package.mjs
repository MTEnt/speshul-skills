#!/usr/bin/env node

import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const FORBIDDEN_KEY = /(?:access[_-]?token|page[_-]?token|user[_-]?token|secret|password|approval[_-]?phrase)/i;
const FORMAT_VALUES = new Set(['text', 'link', 'photo', 'video']);
const STATUS_VALUES = new Set(['draft', 'ready_for_preview', 'manual_handoff', 'scheduled', 'published']);
const QA_PASS = new Set(['passed', 'not_applicable']);

function isObject(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function validAbsoluteUrl(value, protocols = ['http:', 'https:']) {
  if (typeof value !== 'string') return false;
  try {
    return protocols.includes(new URL(value).protocol);
  } catch {
    return false;
  }
}

function scanForbiddenKeys(value, path, errors) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => scanForbiddenKeys(item, `${path}[${index}]`, errors));
    return;
  }
  if (!isObject(value)) return;

  for (const [key, child] of Object.entries(value)) {
    const childPath = path ? `${path}.${key}` : key;
    if (FORBIDDEN_KEY.test(key)) errors.push(`${childPath}: credential or ephemeral approval fields are forbidden`);
    scanForbiddenKeys(child, childPath, errors);
  }
}

function requireObject(value, name, errors) {
  if (!isObject(value)) {
    errors.push(`${name}: must be an object`);
    return {};
  }
  return value;
}

function requireString(value, name, errors) {
  if (typeof value !== 'string' || value.trim() === '') {
    errors.push(`${name}: must be a non-empty string`);
    return '';
  }
  return value;
}

export function validatePostPackage(document, now = Date.now()) {
  const errors = [];
  const warnings = [];

  if (!isObject(document)) return { errors: ['root: must be a JSON object'], warnings };
  scanForbiddenKeys(document, '', errors);

  if (document.schema_version !== '1.0') errors.push('schema_version: expected "1.0"');
  requireString(document.campaign_id, 'campaign_id', errors);
  requireString(document.brand_profile, 'brand_profile', errors);
  if (!STATUS_VALUES.has(document.status)) errors.push(`status: unsupported value ${JSON.stringify(document.status)}`);

  const objective = requireObject(document.objective, 'objective', errors);
  requireString(objective.type, 'objective.type', errors);
  requireString(objective.audience, 'objective.audience', errors);
  requireString(objective.primary_cta, 'objective.primary_cta', errors);

  const page = requireObject(document.page, 'page', errors);
  const pageId = requireString(page.id, 'page.id', errors);
  if (pageId && !/^\d+$/.test(pageId)) errors.push('page.id: must be numeric');
  requireString(page.name, 'page.name', errors);

  const content = requireObject(document.content, 'content', errors);
  if (!FORMAT_VALUES.has(content.format)) errors.push(`content.format: unsupported value ${JSON.stringify(content.format)}`);
  requireString(content.caption, 'content.caption', errors);
  requireString(content.language, 'content.language', errors);
  if (content.link !== null && content.link !== undefined && !validAbsoluteUrl(content.link)) {
    errors.push('content.link: must be null or an absolute HTTP(S) URL');
  }
  if (content.format === 'link' && !validAbsoluteUrl(content.link)) {
    errors.push('content.link: link posts require an absolute HTTP(S) URL');
  }
  if (['photo', 'video'].includes(content.format) && (typeof content.alt_text !== 'string' || content.alt_text.trim() === '')) {
    errors.push('content.alt_text: photo and video packages require meaningful accessibility text');
  }

  if (!Array.isArray(document.media)) {
    errors.push('media: must be an array');
  }
  const media = Array.isArray(document.media) ? document.media : [];
  const seenAssetIds = new Set();
  for (const [index, item] of media.entries()) {
    const asset = requireObject(item, `media[${index}]`, errors);
    const assetId = requireString(asset.asset_id, `media[${index}].asset_id`, errors);
    if (assetId && seenAssetIds.has(assetId)) errors.push(`media[${index}].asset_id: duplicate ${assetId}`);
    seenAssetIds.add(assetId);
    requireString(asset.type, `media[${index}].type`, errors);
    requireString(asset.role, `media[${index}].role`, errors);
    requireString(asset.source, `media[${index}].source`, errors);
    if (asset.approval !== 'approved' && document.status !== 'draft') {
      errors.push(`media[${index}].approval: non-draft packages require approved assets`);
    }
    if (asset.delivery_url !== null && asset.delivery_url !== undefined && !validAbsoluteUrl(asset.delivery_url, ['https:'])) {
      errors.push(`media[${index}].delivery_url: must be null or an HTTPS URL`);
    }
  }

  const publication = requireObject(document.publication, 'publication', errors);
  const transport = publication.transport;
  const action = publication.action;
  if (!['theworkshopai_mcp', 'manual_meta_business_suite'].includes(transport)) {
    errors.push(`publication.transport: unsupported value ${JSON.stringify(transport)}`);
  }
  if (!['publish_now', 'schedule', 'manual_handoff'].includes(action)) {
    errors.push(`publication.action: unsupported value ${JSON.stringify(action)}`);
  }
  if (action === 'schedule') {
    const scheduledTime = Date.parse(publication.scheduled_at);
    if (!Number.isFinite(scheduledTime)) {
      errors.push('publication.scheduled_at: schedule requires an ISO 8601 date and time');
    } else {
      const delay = scheduledTime - now;
      if (delay < 10 * 60 * 1_000 || delay > 30 * 24 * 60 * 60 * 1_000) {
        errors.push('publication.scheduled_at: must be between 10 minutes and 30 days from validation time');
      }
    }
  } else if (publication.scheduled_at !== null && publication.scheduled_at !== undefined) {
    errors.push('publication.scheduled_at: must be null unless action is schedule');
  }

  const primaryImages = media.filter((asset) => isObject(asset) && asset.type === 'image' && asset.role === 'primary');
  const primaryVideos = media.filter((asset) => isObject(asset) && asset.type === 'video' && asset.role === 'primary');
  if (content.format === 'photo') {
    if (primaryImages.length !== 1) errors.push('media: photo format requires exactly one primary image');
    if (transport === 'theworkshopai_mcp' && !validAbsoluteUrl(primaryImages[0]?.delivery_url, ['https:'])) {
      errors.push('media: MCP photo publication requires a primary image with a public HTTPS delivery_url');
    }
  }
  if (content.format === 'video') {
    if (primaryVideos.length !== 1) errors.push('media: video format requires exactly one primary video');
    if (transport !== 'manual_meta_business_suite' || action !== 'manual_handoff') {
      errors.push('publication: current video packages must use manual_meta_business_suite and manual_handoff');
    }
    const thumbnails = media.filter((asset) => isObject(asset) && asset.role === 'thumbnail');
    const captions = media.filter((asset) => isObject(asset) && asset.role === 'captions');
    if (thumbnails.length < 1) errors.push('media: video handoff requires a thumbnail asset');
    if (captions.length < 1) warnings.push('media: add an SRT or transcript asset for the video handoff');
  }
  if (transport === 'theworkshopai_mcp' && !['text', 'link', 'photo'].includes(content.format)) {
    errors.push('publication: theworkshopai_mcp supports only text, link, and photo packages');
  }

  const evidence = requireObject(document.evidence, 'evidence', errors);
  if (!['passed', 'human_review_required'].includes(evidence.claims_review)) {
    errors.push('evidence.claims_review: expected passed or human_review_required');
  }
  if (!Array.isArray(evidence.sources)) errors.push('evidence.sources: must be an array');

  const disclosure = requireObject(document.disclosure, 'disclosure', errors);
  if (!['disclose', 'not_required_with_reason', 'human_review_required'].includes(disclosure.ai)) {
    errors.push('disclosure.ai: unsupported value');
  }
  requireString(disclosure.reason, 'disclosure.reason', errors);
  if (!['confirmed', 'not_applicable', 'human_review_required'].includes(disclosure.identity_consent)) {
    errors.push('disclosure.identity_consent: unsupported value');
  }

  const qa = requireObject(document.qa, 'qa', errors);
  for (const key of ['brand', 'continuity', 'technical', 'policy', 'accessibility']) {
    if (typeof qa[key] !== 'string') errors.push(`qa.${key}: must be a status string`);
  }

  const approvals = requireObject(document.approvals, 'approvals', errors);
  for (const key of ['brief', 'references', 'final_asset', 'final_copy', 'publish']) {
    if (typeof approvals[key] !== 'string') errors.push(`approvals.${key}: must be a status string`);
  }

  if (document.status === 'ready_for_preview') {
    if (evidence.claims_review !== 'passed') errors.push('status: ready_for_preview requires evidence.claims_review=passed');
    if (['human_review_required'].includes(disclosure.ai) || disclosure.identity_consent === 'human_review_required') {
      errors.push('status: ready_for_preview cannot retain disclosure or consent review');
    }
    for (const key of ['brand', 'continuity', 'technical', 'policy', 'accessibility']) {
      if (!QA_PASS.has(qa[key])) errors.push(`status: ready_for_preview requires qa.${key} to pass`);
    }
    for (const key of ['brief', 'references', 'final_asset', 'final_copy']) {
      if (!['approved', 'not_applicable'].includes(approvals[key])) {
        errors.push(`status: ready_for_preview requires approvals.${key} to be approved or not_applicable`);
      }
    }
    if (approvals.publish !== 'pending_mcp_preview') {
      errors.push('status: ready_for_preview requires approvals.publish=pending_mcp_preview');
    }
  }

  if (document.status === 'manual_handoff') {
    if (action !== 'manual_handoff') errors.push('status: manual_handoff requires publication.action=manual_handoff');
    if (approvals.publish !== 'manual_handoff') errors.push('status: manual_handoff requires approvals.publish=manual_handoff');
  }

  if (document.status === 'published' || document.status === 'scheduled') {
    const result = requireObject(publication.result, 'publication.result', errors);
    requireString(result.post_id, 'publication.result.post_id', errors);
  }

  return { errors, warnings };
}

async function main() {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error('Usage: validate-post-package.mjs <post-package.json>');
    process.exitCode = 2;
    return;
  }

  let document;
  try {
    document = JSON.parse(await readFile(filePath, 'utf8'));
  } catch (error) {
    console.error(`Invalid JSON: ${error instanceof Error ? error.message : 'unknown error'}`);
    process.exitCode = 1;
    return;
  }

  const result = validatePostPackage(document);
  for (const warning of result.warnings) console.warn(`Warning: ${warning}`);
  if (result.errors.length > 0) {
    for (const error of result.errors) console.error(`Error: ${error}`);
    process.exitCode = 1;
    return;
  }
  console.log(`Valid post package: ${filePath}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
