from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///history.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean)


with app.app_context():
    # Not needed anymore - Table creation
    # db.create_all()
    # Not needed anymore - Insert data
    # new_task1 = Task(title="She is not a good Muay Thai student", description="She paid the teacher to bully me", done=False)
    # new_task2 = Task(title="I need to keep an eye on Pepper", description="He is taking all the cuddles", done=False)
    # db.session.add(new_task1)
    # db.session.add(new_task2)
    # db.session.commit()

    # Getting all data from DB
    result = db.session.execute(db.select(Task).order_by(Task.id))
    all_task = result.scalars().all()
    board_organisation = [[], [], []]  # col
    row = 0
    col = 0
    for task in all_task:
        board_organisation[col].append(task)
        col += 1
        if col == 3:
            col = 0
            row += 1

    print(board_organisation)

@app.route("/")
def home():
    return render_template("blackboard.html", tasks=board_organisation)


if __name__ == "__main__":
    app.run()
