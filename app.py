import os
from flask import Flask, request, render_template, send_file
from main import run_research

app = Flask(__name__, static_folder='static')

last_filename = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_filename
    summary = ""
    query = ""
    error = ""

    if request.method == 'POST':
        query = request.form.get('query', '').strip()

        if 'clear' in request.form:
            return render_template('index.html')

        elif 'save' in request.form:
            if last_filename and os.path.exists(last_filename):
                return send_file(last_filename, as_attachment=True)
            else:
                error = "⚠️ No file available to download."

        elif query:
            filename = run_research(query)
            last_filename = filename

            if not filename or not os.path.exists(filename):
                error = "❌ Failed to generate research."
            else:
                with open(filename, "r", encoding="utf-8") as f:
                    summary = f.read()
        else:
            error = "❗ Please enter a topic."

    return render_template('index.html', summary=summary, query=query, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host="0.0.0.0", port=port)
