const fs = require('fs');
const path = require('path');

const dataPath = path.join(__dirname, '..', 'src', '_data', 'openclawContrib.json');
const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const errors = [];
const requiredText = value => typeof value === 'string' && value.trim().length > 0;

if (!Number.isInteger(data.mergedPrCount) || data.mergedPrCount < 1) errors.push('mergedPrCount must be a positive integer');
if (!requiredText(data.scope)) errors.push('scope is required');
if (!Number.isInteger(data.latest?.number) || data.latest.number < 1) errors.push('latest.number must be a positive integer');
if (!requiredText(data.latest?.label)) errors.push('latest.label is required');
if (data.latest?.label && /^(feat|fix|chore|refactor)(\([^)]*\))?:/i.test(data.latest.label)) errors.push('latest.label must be reviewed public copy, not a raw commit-style title');
if (data.latest?.url !== `https://github.com/openclaw/openclaw/pull/${data.latest?.number}`) errors.push('latest.url must match latest.number');
if (!/^\d{4}-\d{2}-\d{2}T/.test(data.latest?.mergedAt || '')) errors.push('latest.mergedAt must be an ISO timestamp');
if (data.contributionsUrl !== 'https://github.com/openclaw/openclaw/pulls?q=is%3Apr+author%3Aanyech+is%3Amerged') errors.push('contributionsUrl must be the scoped merged-PR query');
if (data.writingUrl !== '/jingxiao-cai-blog/topics/openclaw-self-hosting.html') errors.push('writingUrl must target the static OpenClaw topic archive');
if (!/^\d{4}-\d{2}-\d{2}$/.test(data.verifiedDate || '')) errors.push('verifiedDate must be YYYY-MM-DD');

const verified = new Date(`${data.verifiedDate}T00:00:00Z`);
const ageDays = (Date.now() - verified.getTime()) / 86400000;
if (!Number.isFinite(ageDays) || ageDays < -1) errors.push('verifiedDate cannot be in the future');
if (ageDays > 45) errors.push(`snapshot is ${Math.floor(ageDays)} days old; refresh or intentionally degrade the metric`);

if (errors.length) {
  console.error(`OpenClaw contribution contract failed:\n- ${errors.join('\n- ')}`);
  process.exit(1);
}

console.log(`OpenClaw contribution contract OK: ${data.mergedPrCount} merged PRs; latest #${data.latest.number}; verified ${data.verifiedDate}.`);
