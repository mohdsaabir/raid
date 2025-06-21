import pdfplumber
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER



with pdfplumber.open("Account_Statement_1243XXXXXX6617.pdf", password="*****") as pdf:
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



    def create_pdf_report(total_withdrawals,total_deposits,final_data,filename="Filtered_Account_Statement.pdf"):

        heading_style = ParagraphStyle(
            name="Heading",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName="Helvetica-Bold"
        )

        # Create the heading paragraph
        heading = Paragraph("Filtered Account Statement", heading_style)



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


        totals_style = styles["Normal"].clone('totals_style')
        totals_style.fontSize=15
        totals_style.leading=30

        totals_para = Paragraph(
            f"<b>Total Withdrawals:</b> Rs {total_withdrawals:,.2f}<br/><b>Total Deposits:</b> Rs {total_deposits:,.2f}",
            totals_style
            )

        pdf.build([heading,Spacer(1,12),table,Spacer(1,15),totals_para])

    create_pdf_report(total_withdrawals,total_deposits,final_data)
    
           
print("Total Withdrawals: ", total_withdrawals)
print("Total Deposits: ", total_deposits)
    



        