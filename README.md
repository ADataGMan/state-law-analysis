# state-law-analysis

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

Only content which appears on the individual law page will be
parsed and tokenized.