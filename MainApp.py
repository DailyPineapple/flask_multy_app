from flask import Flask, render_template
from sub_functions.html_to_pdf import html_to_pdf_bp
from sub_functions.jpg_to_png_convertor import jpg_to_png_bp

app = Flask(__name__)
app.register_blueprint(html_to_pdf_bp, url_prefix='/convert')
app.register_blueprint(jpg_to_png_convertor_bp, url_prefix='/convert')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
