# -*- coding: utf-8 -*-
"""\
This is a python port of "Goose" orignialy licensed to Gravity.com
under one or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.

Python port was written by Xavier Grangier for Recrutae

Gravity.com licenses this file
to you under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from goose.extractors import BaseExtractor


KNOWN_AUTHOR_TAGS = [
    {'attribute': 'itemprop', 'value': 'name', 'content': 'text'}, 
    {'attribute':'class', 'value':'byline_name', 'content': 'text'}
]

class AuthorsExtractor(BaseExtractor):
    def extract(self):
        authors=[]
        for known_meta_tag in KNOWN_AUTHOR_TAGS:
            meta_tags = self.parser.getElementsByTag(
                            self.article.doc,
                            attr=known_meta_tag['attribute'],
                            value=known_meta_tag['value'])
            if meta_tags:
                if known_meta_tag['content'] =='text':
                    authors = map(self.parser.getText, meta_tags)
                else:
                    authors = map(lambda x: self.parser.getAttribute(x, known_meta_tag['content']), meta_tags)
        return list(set(authors))
