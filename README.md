# state_law_analysis

Project for data science exploration of legal data.

## Components

### Binary Retrieval

Capture the data from the state law page as a complete object to
avoid having to retrieve the document from the web repeatedly.

### Tokenize

Parse the binary data from the retrieval effort into meaningful data
to be used for further data science associated projects.

## Design Decisions

### Covered Content

When there are repealed laws which do not have their own page
but are only acknowledged on a higher level summary page,
these will be ignored.

Only content which appears on the page that describes a single
section will be parsed and tokenized.

### Improvement Opportunities

Rather than utitilizing the metadata tags for each section,
the body of the page should be scraped and parsed to create
better coverage. This would improve capture of content and
resolve gaps identified by [Covered Content](#Covered-Content).