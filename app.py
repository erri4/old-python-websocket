from flask import Flask, Response, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/admin')
def admin() -> str:
    """
    return the admin page.
    """
    return render_template('console.html')


@app.route('/')
@app.route('/<custom_page>')
def index(custom_page = None):
    """
    return the main page or redirect to the main page.
    """
    return render_template('index.html') if custom_page is None else redirect(url_for('index'))
