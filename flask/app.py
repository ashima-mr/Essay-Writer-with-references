from flask import Flask, request, jsonify, render_template
from main import create_essay_with_academic_references

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/generate_essay', methods=['POST'])
def generate_essay():
    topic = request.form.get('topic')
    essay, references = create_essay_with_academic_references(topic)
    return render_template('essay.html', essay=essay, references=references)

if __name__ == '__main__':
    app.run(debug=True)

