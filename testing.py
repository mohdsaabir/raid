import pdfplumber
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


with pdfplumber.open("Account_Statement_1243XXXXXX6617.pdf", password="MUHA2708") as pdf:
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
                final_data.append(content)
            elif row == 1 and page_num == 0 :
                continue
            else:
                if all(keyword not in content[2] for keyword in keywords):
                    content[2]=content[2].replace('\n','')
                    try:
                        if content[6]!='':
                            total_withdrawals += float(content[6])
                            final_data.append(content)
                        else:
                            total_deposits += float(content[7]) 
                            final_data.append(content)
                    except ValueError:    
                        final_data.append(content)



    def create_pdf_report(final_data, filename="Filtered_Account_Statement.pdf"):
        pdf = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        normal_style.fontSize = 6
        normal_style.leading = 7

        # Column widths (adjust if needed)
        col_widths = [50, 50, 160, 40, 55, 40, 50, 50, 60, 30]

        # Convert all cells to Paragraphs for wrapping
        processed_data = []
        for row in final_data:
            wrapped_row = [Paragraph(str(cell), normal_style) for cell in row]
            processed_data.append(wrapped_row)

        # Create table
        table = Table(processed_data, colWidths=col_widths)

        # Style the table
        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ])
        table.setStyle(style)

        pdf.build([table])

    create_pdf_report(final_data)
    
           
print("Total Withdrawals: ", total_withdrawals)
print("Total Deposits: ", total_deposits)
    



        