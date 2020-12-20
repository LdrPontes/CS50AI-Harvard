import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_distribution = dict()

    corpus_length = len(corpus)
    
    page_out_length = len(corpus[page])

    random_page_probability = ((1 - damping_factor) / corpus_length)

    for  k in corpus.keys():
        probability_distribution.update({k: random_page_probability})

    if page_out_length >= 0:
        for i in corpus[page]:
            probability_distribution[i] = probability_distribution[i] + (damping_factor / page_out_length)
    else:
        for  k in corpus.keys():
            probability_distribution.update({k: 1 / corpus_length})

    return probability_distribution



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = dict()

    for i in corpus.keys():
        page_rank[i] = 0

    random_page = random.choices(list(corpus.keys()))[0]

    for i in range(n):
        page_rank[random_page] += 1/n

        probabilities = transition_model(corpus, random_page, damping_factor).values()

        random_page = random.choices(list(corpus.keys()), weights = list(probabilities))[0]

    return page_rank
    

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    page_rank = dict()

    inverted_corpus = dict()
    control_changes = True

    
    copy = corpus.copy() #A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself).


    #The function should begin by assigning each page a rank of 1 / N, where N is the total number of pages in the corpus.
    n = len(corpus.keys())
    for i in corpus.keys():
        page_rank[i] = 1 / n

        inverted_corpus[i] = set()

        if(len(corpus[i]) == 0): 
            copy[i] = set(corpus.keys())       
   

    #Create inverted corpus
    for i in copy.keys():
        for j in copy[i]:
            inverted_corpus[j].add(i)

    while(control_changes):
        control_changes = False

        for i in corpus.keys():
            sum = 0

            for j in inverted_corpus[i]:
                length = len(copy[j])
                sum += page_rank[j] / length
            
            prob = ((1 - damping_factor) / n) + (damping_factor * sum)

            difference = abs(page_rank[i] - prob) 
          
            if(difference > 0.001):
                control_changes = True
                
            page_rank[i] = prob
                

    return page_rank
            
if __name__ == "__main__":
    main()
