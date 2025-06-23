import pdfplumber
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER



with pdfplumber.open("Account_Statement_1243XXXXXX6617(1) (1).pdf", password="*****") as pdf:
    total_no_of_pages = len(pdf.pages)
    keywords = ['UPI']
    total_withdrawals=0
    total_deposits=0
    final_data = []
    for page_num, page in enumerate(pdf.pages):
        contents = page.extract_table()
        for row,content in enumerate(contents):
            if page_num == len(pdf.pages) - 1 and row == len(contents) - 1:
                continue
            if row == 0 and page_num == 0:
                content[3] = content[3].replace('\n','')
                content[5] = content[5].replace('\n',' ')
                content[-1] = content[-1].replace('\n','')
                content.pop(-2)
                final_data.append(content)
            elif row == 1 and page_num == 0 :
                continue
            else:
                if all(keyword not in content[2] for keyword in keywords):
                    content[2]=content[2].replace('\n','')
                    content.pop(-2)
                    try:
                        if content[6]!='':
                            total_withdrawals += float(content[6])
                            final_data.append(content)
                        else:
                            total_deposits += float(content[7]) 
                            final_data.append(content)
                    except ValueError:    
                        final_data.append(content)

for data in final_data:
    print(data)