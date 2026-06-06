#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const repoRoot = process.cwd();
const roots = process.argv.slice(2).length ? process.argv.slice(2) : ['src', 'dist'];

const blocked = [
  {
    label: 'generic AI/ML infrastructure positioning',
    pattern: /\bAI\s*\/\s*ML infrastructure\b/i,
    suggest: 'distributed ML runtime systems; backend execution reliability; self-hosted AI-agent operations',
  },
  {
    label: 'generic AI infrastructure positioning',
    pattern: /\bAI infrastructure\b/i,
    suggest: 'distributed ML/AI runtime systems or backend/runtime systems for production ML workloads',
  },
  {
    label: 'generic ML infrastructure positioning',
    pattern: /\bML infrastructure\b/i,
    suggest: 'distributed ML runtime systems or backend/runtime systems for production ML workloads',
  },
  {
    label: 'generic machine-learning infrastructure positioning',
    pattern: /\bmachine learning infrastructure\b/i,
    suggest: 'distributed ML runtime systems or backend/runtime systems for production ML workloads',
  },
  {
    label: 'short-form AI/ML infra positioning',
    pattern: /\b(?:AI|ML|AI\s*\/\s*ML) infra\b/i,
    suggest: 'runtime systems, backend execution, distributed workload reliability, or agent ops',
  },
  {
    label: 'distributed AI/ML infrastructure positioning',
    pattern: /\bdistributed\s+(?:AI|ML|AI\s*\/\s*ML) infrastructure\b/i,
    suggest: 'distributed ML runtime systems and backend execution reliability',
  },
  {
    label: 'old public title phrasing',
    pattern: /\bPrincipal Architect(?: at Oracle)?(?:,| working| specializing)?/i,
    suggest: 'Principal Member of Technical Staff, or omit title when not needed',
  },
  {
    label: 'over-specific HeatWave ML infrastructure phrasing',
    pattern: /\b(?:MySQL\s+)?HeatWave ML infrastructure\b/i,
    suggest: 'HeatWave ML backend/runtime systems, or distributed ML runtime systems when employer detail is not needed',
  },
];

const allowedMarker = 'positioning-drift-allow';
const textExtensions = new Set([
  '.html', '.md', '.njk', '.json', '.xml', '.txt', '.js', '.css', '.yml', '.yaml', '.toml', '.rss', '.atom', '',
]);
const ignoredDirs = new Set(['.git', 'node_modules', 'pagefind', '.cache']);

function walk(target) {
  const abs = path.resolve(repoRoot, target);
  if (!fs.existsSync(abs)) return [];
  const st = fs.statSync(abs);
  if (st.isFile()) return [abs];
  if (!st.isDirectory()) return [];
  const out = [];
  for (const entry of fs.readdirSync(abs, { withFileTypes: true })) {
    if (entry.isDirectory() && ignoredDirs.has(entry.name)) continue;
    const child = path.join(abs, entry.name);
    if (entry.isDirectory()) out.push(...walk(path.relative(repoRoot, child)));
    else if (entry.isFile()) out.push(child);
  }
  return out;
}

function isTextCandidate(file) {
  const rel = path.relative(repoRoot, file).replace(/\\/g, '/');
  if (rel.includes('/pagefind/')) return false;
  const ext = path.extname(file);
  if (textExtensions.has(ext)) return true;
  // Eleventy markdown mirrors are named *.html.md; path.extname handles these as .md.
  return false;
}

const hits = [];
for (const root of roots) {
  for (const file of walk(root).filter(isTextCandidate)) {
    let text;
    try {
      text = fs.readFileSync(file, 'utf8');
    } catch {
      continue;
    }
    const lines = text.split(/\r?\n/);
    for (let i = 0; i < lines.length; i += 1) {
      const line = lines[i];
      const prev = i > 0 ? lines[i - 1] : '';
      if (line.includes(allowedMarker) || prev.includes(allowedMarker)) continue;
      for (const rule of blocked) {
        if (rule.pattern.test(line)) {
          hits.push({
            file: path.relative(repoRoot, file).replace(/\\/g, '/'),
            line: i + 1,
            label: rule.label,
            suggest: rule.suggest,
            text: line.trim(),
          });
        }
      }
    }
  }
}

if (hits.length) {
  console.error(`Positioning drift detected (${hits.length} hit${hits.length === 1 ? '' : 's'}).`);
  console.error('Preferred public positioning: distributed ML runtime systems; backend/runtime systems for production ML workloads; backend execution reliability; self-hosted AI-agent operations.');
  console.error(`If a historical/quoted usage is intentional, add a nearby '${allowedMarker}' comment and keep the context sanitized.`);
  for (const hit of hits) {
    console.error(`\n${hit.file}:${hit.line} [${hit.label}]`);
    console.error(`  ${hit.text}`);
    console.error(`  Suggest: ${hit.suggest}`);
  }
  process.exit(1);
}

console.log(`Positioning drift check passed for ${roots.join(', ')}.`);
