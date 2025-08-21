from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


# 🔹 helper function for search
def get_todos():
    query = request.args.get("q")
    if query:
        return Todo.query.filter(
            (Todo.title.contains(query)) | (Todo.desc.contains(query))
        ).all()
    return Todo.query.all()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form['title']
        desc = request.form['desc']
        deadline_str = request.form.get("deadline")
        deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M") if deadline_str else None

        todo = Todo(title=title, desc=desc, deadline=deadline)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for("todos"))

    # Home only shows form
    return render_template("index2.html")


@app.route("/todos")
def todos():
    allTodo = get_todos()   # 🔹 now supports search here too
    return render_template("todos.html", allTodo=allTodo)


@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    todo = Todo.query.get_or_404(sno)
    if request.method == "POST":
        todo.title = request.form['title']
        todo.desc = request.form['desc']
        deadline_str = request.form.get("deadline")
        todo.deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M") if deadline_str else None

        db.session.commit()
        return redirect(url_for("todos"))
    return render_template("update.html", todo=todo)


@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.get_or_404(sno)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("todos"))   # 🔹 fixed


@app.route("/toggle/<int:sno>")
def toggle(sno):
    todo = Todo.query.get_or_404(sno)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("todos"))   # 🔹 fixed


if __name__ == "__main__":
    app.run(debug=True, port=8000)
