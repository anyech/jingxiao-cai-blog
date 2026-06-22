const markdownIt = require('markdown-it');

function htmlToMarkdownish(value) {
  return String(value || '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<h1[^>]*>([\s\S]*?)<\/h1>/gi, '\n# $1\n')
    .replace(/<h2[^>]*>([\s\S]*?)<\/h2>/gi, '\n## $1\n')
    .replace(/<h3[^>]*>([\s\S]*?)<\/h3>/gi, '\n### $1\n')
    .replace(/<h4[^>]*>([\s\S]*?)<\/h4>/gi, '\n#### $1\n')
    .replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, '\n- $1')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(div|section|article|main|header|footer|table|tr|ul|ol|blockquote)>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[ \t]{2,}/g, ' ')
    .trim();
}

module.exports = function(eleventyConfig) {
  eleventyConfig.setLibrary('md', markdownIt({ html: true, linkify: true, typographer: true }));
  eleventyConfig.addPassthroughCopy({ 'src/assets': 'assets', 'src/public': '.' });
  eleventyConfig.addCollection('posts', function(collectionApi) {
    return collectionApi.getFilteredByGlob(['src/posts/*.md', 'src/posts/*.html']).sort((a, b) => {
      const da = String(a.data.updated || a.data.date || '');
      const db = String(b.data.updated || b.data.date || '');
      const ua = Boolean(a.data.updated && a.data.updated !== a.data.date);
      const ub = Boolean(b.data.updated && b.data.updated !== b.data.date);
      return db.localeCompare(da) || Number(ua) - Number(ub) || String(a.data.title).localeCompare(String(b.data.title));
    });
  });
  eleventyConfig.addFilter('dateDisplay', function(value) {
    if (!value) return '';
    const d = new Date(String(value) + 'T00:00:00Z');
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
  });
  eleventyConfig.addFilter('rfc822', function(value) {
    return new Date(String(value) + 'T00:00:00Z').toUTCString();
  });
  eleventyConfig.addFilter('xmlEscape', function(value) {
    return String(value || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  });
  eleventyConfig.addFilter('json', function(value) {
    return JSON.stringify(value, null, 2);
  });
  eleventyConfig.addFilter('markdownish', htmlToMarkdownish);
  eleventyConfig.addTransform('stripTrailingWhitespace', function(content, outputPath) {
    if (outputPath && /\.(html|md|xml|txt|json)$/.test(outputPath)) {
      return String(content).split('\n').map(line => line.replace(/[ \t]+$/g, '')).join('\n');
    }
    return content;
  });
  return {
    pathPrefix: '/jingxiao-cai-blog/',
    dir: { input: 'src', includes: '_includes', layouts: '_includes', output: 'dist', data: '_data' },
    markdownTemplateEngine: false,
    htmlTemplateEngine: false,
    templateFormats: ['md', 'njk', 'html']
  };
};
