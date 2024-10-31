import streamlit as st
from selenium import webdriver
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from io import BytesIO

# Function to generate high-resolution PNG from Mermaid code
def render_mermaid_to_image(mermaid_code):
    # Set up headless Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    # Render HTML content with Mermaid
    html_content = f"""
    <html>
    <head>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.2.4/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
    </head>
    <body>
        <div class="mermaid">
        {mermaid_code}
        </div>
    </body>
    </html>
    """
    driver.get("data:text/html;charset=utf-8," + html_content)

    # Set high resolution for the screenshot
    driver.set_window_size(2000, 2000)  # Adjust size for higher resolution
    driver.implicitly_wait(3)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()

    # Convert screenshot to PIL Image for display in Streamlit
    image = Image.open(BytesIO(screenshot))
    return image

# Function to generate PDF from high-resolution image
def generate_pdf_from_image(image):
    pdf_buffer = BytesIO()
    page_width, page_height = letter
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    # Calculate scaling to fit the image within the page
    img_width, img_height = image.size
    scale_factor = min(page_width / img_width, (page_height - 100) / img_height)  # Leave top margin

    # Calculate centered position for the scaled image
    img_width_scaled = img_width * scale_factor
    img_height_scaled = img_height * scale_factor
    x_position = (page_width - img_width_scaled) / 2
    y_position = (page_height - img_height_scaled) / 2

    # Save image to temporary file in high DPI
    temp_image_path = "temp_image.png"
    image.save(temp_image_path, format="PNG", dpi=(300, 300))  # High DPI for quality
    
    # Draw the image centered and scaled
    c.drawImage(temp_image_path, x_position, y_position, width=img_width_scaled, height=img_height_scaled)
    c.showPage()
    c.save()
    
    # Clean up and return PDF
    pdf_buffer.seek(0)
    os.remove(temp_image_path)
    return pdf_buffer.getvalue()

# Streamlit app UI
st.title("Mermaid Diagram Visualizer and PDF Exporter")

mermaid_code = st.text_area("Enter your Mermaid code here:", height=200, 
                            placeholder="graph TD\nA-->B\nB-->C\nC-->D")

if mermaid_code:
    image = render_mermaid_to_image(mermaid_code)
    
    # Display the image preview in Streamlit
    st.image(image, caption="Mermaid Diagram Preview", use_column_width=True)
    
    if st.button("Generate PDF"):
        pdf_data = generate_pdf_from_image(image)
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name="mermaid_diagram.pdf",
            mime="application/pdf"
        )
