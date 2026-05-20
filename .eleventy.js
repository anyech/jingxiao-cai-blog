const markdownIt = require('markdown-it');

module.exports = function(eleventyConfig) {
  eleventyConfig.setLibrary('md', markdownIt({ html: true, linkify: true, typographer: true }));
  eleventyConfig.addPassthroughCopy({ 'src/assets': 'assets', 'src/public': '.' });
  eleventyConfig.addCollection('posts', function(collectionApi) {
    return collectionApi.getFilteredByGlob(['src/posts/*.md', 'src/posts/*.html']).sort((a, b) => {
      const da = String(a.data.updated || a.data.date || '');
      const db = String(b.data.updated || b.data.date || '');
      return db.localeCompare(da) || String(a.data.title).localeCompare(String(b.data.title));
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
  return {
    pathPrefix: '/jingxiao-cai-blog/',
    dir: { input: 'src', includes: '_includes', layouts: '_includes', output: 'dist', data: '_data' },
    markdownTemplateEngine: false,
    htmlTemplateEngine: false,
    templateFormats: ['md', 'njk', 'html']
  };
};
