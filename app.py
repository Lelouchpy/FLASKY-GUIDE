from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text, DateTime
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quotes.db"
app.secret_key = "quote_app_secret"

class Base(DeclarativeBase): pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Quote(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # Keep this for existing database
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

@app.route("/")
def home():
    quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    return render_template("quote.html", quotes=quotes)

@app.route("/quotes/new", methods=["GET", "POST"])
def create_quote():
    if request.method == "POST":
        text, author = request.form["text"], request.form["author"]
        if not text or not author:
            flash("Quote and author are required")
            return redirect(url_for("create_quote"))
        
        quote = Quote(text=text, author=author, user_id=1)  # Include user_id here
        db.session.add(quote)
        db.session.commit()
        flash("Quote added")
        return redirect(url_for("home"))
    return render_template("edit.html")

@app.route("/quotes/<int:id>")
def view_quote(id):
    quote = Quote.query.get_or_404(id)
    return render_template("quote_view.html", quote=quote)

@app.route("/quotes/<int:id>/edit", methods=["GET", "POST"])
def edit_quote(id):
    quote = Quote.query.get_or_404(id)
    
    if request.method == "POST":
        quote.text = request.form["text"]
        quote.author = request.form["author"]
        db.session.commit()
        flash("Quote updated")
        return redirect(url_for("view_quote", id=quote.id))
    
    return render_template("edit.html", quote=quote)

@app.route("/quotes/<int:id>/delete")
def delete_quote(id):
    quote = Quote.query.get_or_404(id)
    db.session.delete(quote)
    db.session.commit()
    flash("Quote deleted")
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)