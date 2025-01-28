from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageTemplate,
    Frame,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# Function to add page number at the bottom center of the page
def add_page_number(canvas, doc):
    page_number = f"Page {doc.page}"
    canvas.setFont("Helvetica", 10)
    canvas.drawString(A4[0] / 2 - 20, 20, page_number)


# Function to create the picking list
def create_picking_list(filename, customer_info, line_items):

    margin = 36

    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    # Define a frame for the content area
    frame = Frame(margin, margin, A4[0] - 2 * margin, A4[1] - 2 * margin, id="normal")

    # Define the page template (this includes the frame)
    def on_page(canvas, doc):
        add_page_number(canvas, doc)

    page_template = PageTemplate(id="normal", frames=frame, onPage=on_page)

    # Add this page template to the document
    pdf.addPageTemplates([page_template])

    elements = []

    # Styles
    styles = getSampleStyleSheet()
    header_style = styles["Heading2"]
    normal_style = styles["Normal"]
    title_style = styles["Title"]

    # Add title
    elements.append(Paragraph("Picking List", title_style))
    elements.append(Spacer(1, 12))

    # Add header section
    elements.append(Paragraph(f"Customer: {customer_info['name']}", header_style))
    elements.append(
        Paragraph(f"Order Number: {customer_info['order_number']}", normal_style)
    )
    elements.append(
        Paragraph(f"Delivery Date: {customer_info['delivery_date']}", normal_style)
    )
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Picked By: ________________________", normal_style))
    elements.append(Spacer(1, 20))

    # Create the line items table
    table_data = [
        ["Item", "Name", "Product Code", "Quantity", "Location", "Bay", "Picked"]
    ]
    table_data.extend(line_items)

    # Calculate table column widths to fit within margins
    page_width = A4[0] - 2 * margin
    col_widths = [
        page_width * 0.096,
        page_width * 0.3,
        page_width * 0.22,
        page_width * 0.096,
        page_width * 0.096,
        page_width * 0.096,
        page_width * 0.096,
    ]

    # Create the table
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ]
        )
    )

    elements.append(table)
    pdf.build(elements)
