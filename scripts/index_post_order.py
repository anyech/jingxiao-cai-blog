#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

MONTH_DATE_RE = re.compile(
    r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
)
POST_BLOCK_RE = re.compile(r'<div class="post">.*?</div>', re.S)
TITLE_RE = re.compile(r'<h3><a [^>]*>(.*?)</a></h3>', re.S)
DATE_RE = re.compile(r'<p class="date">(.*?)</p>', re.S)


@dataclass
class PostBlock:
    block: str
    title: str
    publish_date: datetime
    effective_date: datetime


def parse_post_block(block: str) -> PostBlock:
    title_match = TITLE_RE.search(block)
    date_match = DATE_RE.search(block)
    if not title_match or not date_match:
        raise ValueError('Could not parse title/date from index post block')

    title = re.sub(r'\s+', ' ', title_match.group(1)).strip()
    date_text = re.sub(r'\s+', ' ', date_match.group(1)).strip()
    date_strings = MONTH_DATE_RE.findall(date_text)
    # MONTH_DATE_RE with a capturing group returns only the month names via findall,
    # so use finditer to get full matches.
    full_dates = [m.group(0) for m in MONTH_DATE_RE.finditer(date_text)]
    if not full_dates:
        raise ValueError(f'No recognizable dates in date text: {date_text!r}')

    publish_date = datetime.strptime(full_dates[0], '%B %d, %Y')
    effective_date = datetime.strptime(full_dates[-1], '%B %d, %Y')
    return PostBlock(block=block, title=title, publish_date=publish_date, effective_date=effective_date)


def load_blocks(index_path: Path) -> tuple[str, list[PostBlock], str]:
    text = index_path.read_text()
    start_marker = '<h2>Blog Posts</h2>'
    end_marker = '  <hr>'
    start = text.find(start_marker)
    end = text.find(end_marker, start)
    if start == -1 or end == -1:
        raise ValueError('Could not locate blog post list boundaries in index.html')

    body_start = start + len(start_marker)
    prefix = text[:body_start]
    middle = text[body_start:end]
    suffix = text[end:]

    raw_blocks = POST_BLOCK_RE.findall(middle)
    if not raw_blocks:
        raise ValueError('No post blocks found in index.html')

    posts = [parse_post_block(block) for block in raw_blocks]
    return prefix, posts, suffix


def sorted_posts(posts: list[PostBlock]) -> list[PostBlock]:
    return sorted(
        posts,
        key=lambda p: (
            p.effective_date,
            p.publish_date,
            p.title.lower(),
        ),
        reverse=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate or rewrite index.html post ordering by effective recency.')
    parser.add_argument('--index', default='index.html', help='Path to index.html (default: index.html)')
    parser.add_argument('--write', action='store_true', help='Rewrite index.html into sorted order')
    args = parser.parse_args()

    index_path = Path(args.index)
    prefix, posts, suffix = load_blocks(index_path)
    desired = sorted_posts(posts)

    current_titles = [p.title for p in posts]
    desired_titles = [p.title for p in desired]

    if current_titles == desired_titles:
        print('index order OK')
        return 0

    print('index order mismatch:')
    for i, (current, wanted) in enumerate(zip(current_titles, desired_titles), start=1):
        if current != wanted:
            print(f'  {i}. current={current!r}')
            print(f'     wanted={wanted!r}')

    if not args.write:
        return 1

    middle = '\n\n' + '\n\n'.join(p.block for p in desired) + '\n\n'
    index_path.write_text(prefix + middle + suffix)
    print(f'rewrote {index_path} in effective-recent-first order')
    return 0


if __name__ == '__main__':
    sys.exit(main())
