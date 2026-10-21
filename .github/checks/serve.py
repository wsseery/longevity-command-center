"""Static server for the playwright check that resolves clean URLs the way Netlify does.

  serve.py <port> <directory>

The site links to /news, /blog-... (clean URLs, canonical since 2026-10-20). Netlify serves
/news from news.html; `python3 -m http.server` does not, so every internal link would read
as broken. This serves <path>.html when <path> itself does not exist, and nothing else
differs from http.server. Netlify's forced .html -> clean 301s (netlify.toml) are not
emulated: both forms answer 200 here.
"""

import functools
import http.server
import os
import sys


class CleanUrlHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        local = super().translate_path(path)
        if not os.path.exists(local) and os.path.isfile(local + ".html"):
            return local + ".html"
        return local

    def log_message(self, *args):
        pass


def main():
    port, directory = int(sys.argv[1]), sys.argv[2]
    handler = functools.partial(CleanUrlHandler, directory=directory)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    main()
