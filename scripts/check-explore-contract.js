const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const dist = path.join(root, 'dist');
const search = fs.readFileSync(path.join(dist, 'search.html'), 'utf8');
const home = fs.readFileSync(path.join(dist, 'index.html'), 'utf8');
const topics = JSON.parse(fs.readFileSync(path.join(root, 'src', '_data', 'topics.json'), 'utf8'));
const postCount = fs.readdirSync(path.join(root, 'src', 'posts')).filter(file => /\.(html|md)$/.test(file)).length;
const errors = [];

function expect(condition, message) {
  if (!condition) errors.push(message);
}

expect((search.match(/data-explore-card/g) || []).length === postCount, `Explore must render all ${postCount} posts without JavaScript`);
for (const control of ['q', 'topic', 'tag', 'year', 'month', 'sort']) {
  expect(search.includes(`data-filter="${control}"`), `Explore is missing ${control} control`);
}
expect(search.includes('assets/explore.js'), 'Explore script is not loaded');
expect(!search.includes('new PagefindUI'), 'Legacy standalone Pagefind UI must not remain');
expect(home.includes('class="author-card"'), 'Homepage is missing the author card');
expect(home.includes('Personal website') && home.includes('LinkedIn') && home.includes('GitHub'), 'Homepage is missing public profile links');
expect((home.match(/class="topic-card"/g) || []).length === topics.length, `Homepage must render ${topics.length} topic cards`);
expect((home.match(/class="post-card"/g) || []).length === 9, 'Homepage must render exactly 9 latest publication cards');
expect(fs.existsSync(path.join(dist, 'pagefind', 'pagefind.js')), 'Pagefind JavaScript index is missing');
expect(fs.existsSync(path.join(dist, 'feed.xml')), 'RSS feed is missing');
expect(fs.existsSync(path.join(dist, 'sitemap.xml')), 'Sitemap is missing');
expect(fs.existsSync(path.join(dist, 'llms.txt')), 'llms.txt is missing');
expect(search.includes('google-site-verification'), 'Google site verification must remain in generated pages');

for (const topic of topics) {
  expect(fs.existsSync(path.join(dist, 'topics', `${topic.slug}.html`)), `Static topic page missing: ${topic.slug}`);
}

if (errors.length) {
  console.error(`Explore contract failed with ${errors.length} error(s):\n- ${errors.join('\n- ')}`);
  process.exit(1);
}

console.log(`Explore contract OK: ${postCount} static cards, ${topics.length} topic pages, Pagefind and generated surfaces present.`);
