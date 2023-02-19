from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

model_name = "deepset/roberta-large-squad2"
qa_pipeline = pipeline("question-answering", model=model_name, tokenizer=model_name)

nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
qa1 = {
    'question': 'What is EPAM?',
    'context': 'EPAM Systems, Inc. is an American company that specializes in software engineering services, digital platform engineering, and digital product design, operating out of Newtown, Pennsylvania. EPAM is a founding member of the MACH Alliance.'
}
qa2 = {
    'question': 'What is EPAM?',
    'context': 'Genworth Financial is an S&P 400 insurance company. The firm was founded as The Life Insurance Company of Virginia in 1871.[5] In 1986, Life of Virginia was acquired by Combined Insurance, which became Aon plc in 1987.[6] In 1996, Life of Virginia was sold to GE Capital.[7] In May 2004, Genworth Financial was formed out of various insurance businesses of General Electric in the largest IPO of that year.[8] Genworth Financial is incorporated in Virginia.[9]'
}
qa3 = {
    'question': 'What is EPAM?',
    'context': 'Susquehanna lowered the firm’s price target on Epam Systems to $410 from $462 and keeps a Positive rating on the shares. The analyst said they continue to demonstrate that its unique engineering culture wins in the best and worst of times, but it is not immune to macro conditions and experienced softer demand than expected with two major customers.'
}
res = nlp(qa1)
print(res)

res = nlp(qa2)
print(res)

res = nlp(qa3)
print(res)