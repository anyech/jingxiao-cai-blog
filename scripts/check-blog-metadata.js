const fs = require('fs');
const path = require('path');

const postsDir = path.join(__dirname, '..', 'src', 'posts');
const topics = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'src', '_data', 'topics.json'), 'utf8'));
const topicSlugs = new Set(topics.map(topic => topic.slug));
const files = fs.readdirSync(postsDir).filter(file => /\.(html|md)$/.test(file)).sort();
const seenSlugs = new Map();
const distribution = new Map([...topicSlugs].map(slug => [slug, 0]));
const errors = [];
const isoDate = /^\d{4}-\d{2}-\d{2}$/;

function frontmatter(source) {
  const match = source.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return undefined;
  const values = {};
  for (const line of match[1].split('\n')) {
    const field = line.match(/^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$/);
    if (!field) continue;
    values[field[1]] = field[2].trim().replace(/^(['"])([\s\S]*)\1$/, '$2').replace(/''/g, "'");
  }
  return values;
}

for (const file of files) {
  const data = frontmatter(fs.readFileSync(path.join(postsDir, file), 'utf8'));
  if (!data) {
    errors.push(`${file}: missing frontmatter`);
    continue;
  }
  for (const field of ['title', 'slug', 'description', 'summary', 'date', 'topic', 'tags']) {
    if (!data[field]) errors.push(`${file}: missing ${field}`);
  }
  if (!isoDate.test(data.date || '')) errors.push(`${file}: date must be YYYY-MM-DD`);
  if (data.updated && !isoDate.test(data.updated)) errors.push(`${file}: updated must be empty or YYYY-MM-DD`);
  if (data.updated && data.updated <= data.date) errors.push(`${file}: updated must be later than date`);
  if (!topicSlugs.has(data.topic)) errors.push(`${file}: unknown topic ${data.topic || '(empty)'}`);
  else distribution.set(data.topic, distribution.get(data.topic) + 1);
  if (seenSlugs.has(data.slug)) errors.push(`${file}: duplicate slug also used by ${seenSlugs.get(data.slug)}`);
  else seenSlugs.set(data.slug, file);
  if (data.tags && !/^\[.*\]$/.test(data.tags)) errors.push(`${file}: tags must remain an inline array`);
}

for (const topic of topics) {
  const count = distribution.get(topic.slug);
  if (count === 0) errors.push(`topic ${topic.slug}: has no posts`);
  if (count > Math.ceil(files.length * 0.5)) errors.push(`topic ${topic.slug}: ${count}/${files.length} posts is too broad`);
}

if (errors.length) {
  console.error(`Metadata contract failed with ${errors.length} error(s):\n- ${errors.join('\n- ')}`);
  process.exit(1);
}

console.log(`Metadata contract OK: ${files.length} posts, ${topics.length} topics, ${seenSlugs.size} unique slugs.`);
for (const topic of topics) console.log(`- ${topic.label}: ${distribution.get(topic.slug)}`);
