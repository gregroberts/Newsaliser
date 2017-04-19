import nltk
from nltk.corpus import stopwords
from collections import Counter


if __name__ == '__main__':
	#download required corpora
	nltk.download('stopwords')
	nltk.download('maxent_treebank_pos_tagger')

try:
    stopwords = stopwords.words('english')
except:
    stopwords = []

# Used when tokenizing words
sentence_re = r'''(?x)      # set flag to allow verbose regexps
      ([A-Z])(\.[A-Z])+\.?  # abbreviations, e.g. U.S.A.
    | \w+(-\w+)*            # words with optional internal hyphens
    | \$?\d+(\.\d+)?%?      # currency and percentages, e.g. $12.40, 82%
    | \.\.\.                # ellipsis
    | [][.,;"'?():-_`]      # these are separate tokens
'''

grammar = r"""
    NBAR:
        (<DT>?<RB>?)?<JJ.*|CD>*(<JJ.*|CD>)*{<NNP.*>+} # Nouns and Adjectives, terminated with Nouns
        
    NP:
        {<NBAR>+}
        {<NBAR>+<RP|IN|TO|CD|DT><NBAR>+}  # Above, connected with in/of/etc...
"""

lemmatizer = nltk.WordNetLemmatizer()
stemmer = nltk.stem.porter.PorterStemmer()
chunker = nltk.RegexpParser(grammar)



def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    for subtree in tree.subtrees(filter = lambda t: t.node=='NP'):
        yield subtree.leaves()

def normalise(word):
    """Normalises words to lowercase and stems and lemmatizes it."""
    word = word.lower()
    #word = stemmer.stem_word(word)
    word = lemmatizer.lemmatize(word)
    return word

def acceptable_word(word):
    """Checks conditions for acceptable word: length, stopword."""
    accepted = bool(2 <= len(word) <= 40
        and word.lower() not in stopwords)
    return accepted


def get_terms(tree):
    for leaf in leaves(tree):
        term = []
        for w, t in leaf:
            if acceptable_word(w) and normalise(w) not in term:
                term.append(normalise(w))
        #term = [ normalise(w) for w,t in leaf if acceptable_word(w) ]
        yield term


def get_nounphrases(text):
	toks = nltk.regexp_tokenize(text, sentence_re)
	postoks = nltk.tag.pos_tag(toks)
	tree = chunker.parse(postoks)
	terms = get_terms(tree)
	return filter(
	        lambda x: (1<len(x[0].split(' ')) or x[1]>1) and len(x[0])>3,
	        Counter(
	            map(
	                lambda x: ' '.join(x).title(),
	                terms
	            )
	    ).most_common()
	)
