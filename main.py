from flask import Flask, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date, datetime
from flask_bootstrap import Bootstrap4
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///history.db"
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(model_class=Base)
db.init_app(app)
bootstrap = Bootstrap4(app)


class Category(db.Model):
    __tablename__ = "category"  # Table name
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Relationship to Task
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="category")


class Task(db.Model):
    __tablename__ = "task"  # Table name
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    category_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("category.id"), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship to Category
    category: Mapped["Category"] = relationship("Category", back_populates="tasks")
class MyForm(FlaskForm):
    Title = StringField('Title', validators=[DataRequired()])
    Category = SelectField('Category', choices=[], validators=[Optional()])
    Date = DateField('Date', validators=[Optional()])
    Description = StringField('Description ')
    Submit = SubmitField('Submit')

class Catform(FlaskForm):
    CatName = StringField('Category', validators=[DataRequired()])
    Submit = SubmitField('Submit')


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    # Getting all data from DB
    result = db.session.execute(db.select(Task).order_by(Task.id))
    all_task = result.scalars().all()
    done_board = [[], [], []]  # col
    todo_board = [[], [], []]
    todo_row = 0
    todo_col = 0
    done_row = 0
    done_col = 0
    for task in all_task:
        if not task.done:
            todo_board[todo_col].append(task)
            todo_col += 1
            if todo_col == 3:
                todo_col = 0
                todo_row += 1
        else:
            done_board[done_col].append(task)
            done_col += 1
            if done_col == 3:
                done_col = 0
                done_row += 1
    today = datetime.date(datetime.today())
    print(today)
    return render_template("blackboard.html", todo_tasks=todo_board, done_tasks=done_board, today=today)


@app.route("/done/<task_id>")
def done(task_id):
    print(task_id)
    with app.app_context():
        updated_task = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()
        if updated_task.done:
            updated_task.done = False
        else:
            updated_task.done = True
        db.session.commit()
    return redirect('/')


@app.route("/edit/<task_id>", methods=["GET", "POST"])
def edit(task_id):
    form = MyForm()
    toEdit_task = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()
    form.Category.choices = [("", "Uncategorized")] + [(str(c.id), c.name) for c in
                                                       db.session.execute(db.select(Category)).scalars().all()]

    if not toEdit_task:
        flash("Task not found!", "error")
        return redirect("/")
    if form.validate_on_submit():
        toEdit_task.title = form.Title.data
        toEdit_task.category_id = int(form.Category.data) if form.Category.data and form.Category.data != "" else None
        toEdit_task.date = form.Date.data if form.Date.data else None
        toEdit_task.description = form.Description.data
        db.session.commit()
        return redirect('/')
    else:
        form.Title.data = toEdit_task.title
        form.Date.data = toEdit_task.date
        form.Description.data = toEdit_task.description
        form.Category.data = str(toEdit_task.category_id) if toEdit_task.category_id else ""

    return render_template("edit.html", form=form, task=toEdit_task)


@app.route('/new', methods=["GET", "POST"])
def new():
    form = MyForm()
    if form.validate_on_submit():
        cat_value = None
        if form.Category.data:
            # TODO translate value from category into category_ID
            cat_value = form.Category.data
        print(f"{form.Title.data}, cat{form.Category.data}, date:{form.Date.data}, {form.Description.data}")
        new_task = Task(title=form.Title.data, category=cat_value, date=form.Date.data,
                        description=form.Description.data)
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    form.Category.choices = [("", "Uncategorized")] + [(str(c.id), c.name) for c in db.session.execute(db.select(Category)).scalars().all()]
    return render_template('new.html', form=form)


@app.route('/delete/<task_id>')
def delete(task_id):
    to_delete = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/')


@app.route('/categories', methods=["GET", "POST"])
def categories():
    # Query all categories from the "category" database
    form = Catform()
    categories = db.session.execute(db.select(Category)).scalars().all()

    if form.validate_on_submit():
        new_cat = Category(name=form.CatName.data.capitalize())
        db.session.add(new_cat)
        db.session.commit()
        return redirect('/categories')

    return render_template('categories.html', categories=categories, form=form)

@app.route('/del_cat/<cat_id>')
def del_cat(cat_id):
    to_delete = db.session.execute(db.select(Category).where(Category.id == cat_id)).scalar()
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/categories')

@app.route('/up_cat/<cat_id>', methods=["GET", "POST"])
def up_cat(cat_id):
    form = Catform()
    to_update = db.session.execute(db.select(Category).where(Category.id == cat_id)).scalar()
    if form.validate_on_submit():
        to_update.name = form.CatName.data.capitalize()
        db.session.commit()
        return redirect('/categories')
    else:
        form.CatName.data = to_update.name
    return render_template('update_cat.html', form=form)


if __name__ == "__main__":
    app.run()
