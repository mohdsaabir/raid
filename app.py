import pdfplumber
import tempfile
import io
from flask import Flask, render_template, request, send_file, flash
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "secretsuperkey"

@app.route('/', methods=["GET","POST"])
def index():
    if request.method=="POST":
        pdf_file = request.files["pdf_file"]
        password = request.form["password"]

        if not pdf_file or not password:
            flash("Please upload a file and enter password.")
            return render_template("index.html")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
                file_name = secure_filename(pdf_file.filename)
                pdf_file.save(tmp_input.name)

            with pdfplumber.open(tmp_input.name , password=password) as pdf:
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
                            
            buffer = create_pdf_report(total_withdrawals,total_deposits,final_data)
            return send_file(buffer, as_attachment=True, download_name="Filtered_statment.pdf", mimetype='application/pdf')
                
        except Exception as e:
            flash(f"Error: {str(e)}")
            return render_template("index.html")
    
    return render_template("index.html")


def create_pdf_report(total_withdrawals,total_deposits,final_data):
        
        buffer = io.BytesIO()

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
            buffer,
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
        col_widths = [50, 50, 160, 40, 55, 40, 50, 50, 30]

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
        buffer.seek(0)
        return buffer



if __name__ == '__main__':
    app.run(debug=True)