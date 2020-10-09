import re

from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.preprocessor.utils import convert_files_to_dicts


def clean_wiki_text(text: str) -> str:
    # get rid of multiple new lines
    while "\n\n" in text:
        text = text.replace("\n\n", "\n")

    # remove extremely short lines
    lines = text.split("\n")
    cleaned = []
    for l in lines:
        if len(l) > 30:
            cleaned.append(l)
        elif l[:2] == "==" and l[-2:] == "==":
            cleaned.append(l)
    text = "\n".join(cleaned)

    # add paragraphs (identified by wiki section title which is always in format "==Some Title==")
    text = text.replace("\n==", "\n\n\n==")

    # remove empty paragrahps
    text = re.sub(r"(==.*==\n\n\n)", "", text)

    return text


document_store = ElasticsearchDocumentStore(host="localhost", scheme="http",
                                            index="sec")

doc_dir = "data/sec"
# Convert files to dicts
# You can optionally supply a cleaning function that is applied to each doc (e.g. to remove footers)
# It must take a str as input, and return a str.
dicts = convert_files_to_dicts(dir_path=doc_dir, clean_func=clean_wiki_text, split_paragraphs=True)

# We now have a list of dictionaries that we can write to our document store.
# If your texts come from a different source (e.g. a DB), you can of course skip convert_files_to_dicts() and create the dictionaries yourself.
# The default format here is: {"name": "<some-document-name>, "text": "<the-actual-text>"}
# (Optionally: you can also add more key-value-pairs here, that will be indexed as fields in Elasticsearch and
# can be accessed later for filtering or shown in the responses of the Finder)

# Let's have a look at the first 3 entries:
print(dicts[:3])

# Now, let's write the dicts containing documents to our DB.
document_store.write_documents(dicts)
