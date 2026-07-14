const markdownIt = require('markdown-it');

function decodeHtmlEntities(value) {
  const named = {
    amp: '&',
    apos: "'",
    bull: '•',
    gt: '>',
    larr: '←',
    lt: '<',
    mdash: '—',
    nbsp: ' ',
    ndash: '–',
    quot: '"'
  };

  return String(value || '').replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (match, entity) => {
    if (entity[0] === '#') {
      const radix = entity[1].toLowerCase() === 'x' ? 16 : 10;
      const digits = radix === 16 ? entity.slice(2) : entity.slice(1);
      const codePoint = Number.parseInt(digits, radix);
      return Number.isFinite(codePoint) ? String.fromCodePoint(codePoint) : match;
    }
    return named[entity.toLowerCase()] ?? match;
  });
}

function inlineHtmlToMarkdown(value) {
  return decodeHtmlEntities(String(value || '')
    .replace(/<a\b[^>]*href=(['"])(.*?)\1[^>]*>([\s\S]*?)<\/a>/gi, (_match, _quote, href, text) => {
      return `[${inlineHtmlToMarkdown(text)}](${decodeHtmlEntities(href)})`;
    })
    .replace(/<(strong|b)\b[^>]*>([\s\S]*?)<\/\1>/gi, '**$2**')
    .replace(/<(em|i)\b[^>]*>([\s\S]*?)<\/\1>/gi, '*$2*')
    .replace(/<code\b[^>]*>([\s\S]*?)<\/code>/gi, '`$1`')
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]+>/g, ''))
    .replace(/\|/g, '\\|')
    .replace(/\s+/g, ' ')
    .trim();
}

function htmlTableToMarkdown(tableHtml) {
  const rows = [...String(tableHtml || '').matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)]
    .map(row => [...row[1].matchAll(/<(th|td)\b[^>]*>([\s\S]*?)<\/\1>/gi)]
      .map(cell => inlineHtmlToMarkdown(cell[2])));

  if (!rows.length || !rows[0].length) return '';

  const width = Math.max(...rows.map(row => row.length));
  const normalized = rows.map(row => [...row, ...Array(width - row.length).fill('')]);
  const renderRow = row => `| ${row.join(' | ')} |`;
  return [
    renderRow(normalized[0]),
    renderRow(Array(width).fill('---')),
    ...normalized.slice(1).map(renderRow)
  ].join('\n');
}

function htmlToMarkdownish(value) {
  const protectedBlocks = [];
  const protect = block => {
    const token = `MARKDOWNISH_BLOCK_${protectedBlocks.length}_TOKEN`;
    protectedBlocks.push({ token, block });
    return `\n\n${token}\n\n`;
  };

  let markdownish = String(value || '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<pre\b[^>]*>\s*<code\b([^>]*)>([\s\S]*?)<\/code>\s*<\/pre>/gi, (_match, attrs, code) => {
      const language = String(attrs || '').match(/\blanguage-([a-z0-9_-]+)/i)?.[1] || '';
      const decoded = decodeHtmlEntities(code).replace(/^\n|\n$/g, '');
      const longestFence = Math.max(0, ...[...decoded.matchAll(/`+/g)].map(match => match[0].length));
      const fence = '`'.repeat(Math.max(3, longestFence + 1));
      return protect(`${fence}${language}\n${decoded}\n${fence}`);
    })
    .replace(/<table\b[^>]*>([\s\S]*?)<\/table>/gi, (_match, table) => protect(htmlTableToMarkdown(table)))
    .replace(/<a\b[^>]*href=(['"])(.*?)\1[^>]*>([\s\S]*?)<\/a>/gi, (_match, _quote, href, text) => {
      return `[${inlineHtmlToMarkdown(text)}](${decodeHtmlEntities(href)})`;
    })
    .replace(/<(strong|b)\b[^>]*>([\s\S]*?)<\/\1>/gi, '**$2**')
    .replace(/<(em|i)\b[^>]*>([\s\S]*?)<\/\1>/gi, '*$2*')
    .replace(/<code\b[^>]*>([\s\S]*?)<\/code>/gi, '`$1`')
    .replace(/<h1[^>]*>([\s\S]*?)<\/h1>/gi, '\n# $1\n')
    .replace(/<h2[^>]*>([\s\S]*?)<\/h2>/gi, '\n## $1\n')
    .replace(/<h3[^>]*>([\s\S]*?)<\/h3>/gi, '\n### $1\n')
    .replace(/<h4[^>]*>([\s\S]*?)<\/h4>/gi, '\n#### $1\n')
    .replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, '\n- $1')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(div|section|article|main|header|footer|table|tr|ul|ol|blockquote)>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, match => decodeHtmlEntities(match))
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[ \t]{2,}/g, ' ')
    .trim();

  for (const { token, block } of protectedBlocks) {
    markdownish = markdownish.replace(token, block);
  }

  return markdownish;
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
