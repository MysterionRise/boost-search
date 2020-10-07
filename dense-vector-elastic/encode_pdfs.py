import base64
import glob
import requests
from PyPDF2 import PdfFileWriter, PdfFileReader

orig_path = "../dense-vector-elastic/pdfs/*.pdf"

# for fname in glob.glob(orig_path):
#     filename = fname.split('/')[2]
#     inputpdf = PdfFileReader(open(fname, "rb"))
#
#     for i in range(inputpdf.numPages):
#         output = PdfFileWriter()
#         output.addPage(inputpdf.getPage(i))
#         with open("../pages-pdfs/{}-{}.pdf".format(filename, i), "wb") as outputStream:
#             output.write(outputStream)

id = 0

pages_path = "../dense-vector-elastic/pages-pdfs/*.pdf"

for fname in glob.glob(pages_path):
    print(fname)
    with open(fname, 'rb') as f:
        data = base64.b64encode(f.read()).decode('ascii')
    r = requests.put('http://192.168.8.101:9200/pdfs/_doc/{}?pipeline=pdf-indexing'.format(id),
                      json = {
                          "data": data
                      })
    id += 1

