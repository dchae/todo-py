from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    session,
    request,
    flash,
    g,
)
import todos.utils as utils

app = Flask(__name__)
app.secret_key = "dev_secret"


@app.context_processor
def list_utilities_processor():
    return dict(list_is_completed=utils.list_is_completed)


@app.before_request
def initialize_session():
    if "lists" not in session:
        session["lists"] = {}
    g.lists = session["lists"]


@app.route("/")
def index():
    return redirect(url_for("get_lists"))


@app.route("/lists")
def get_lists():
    lists = utils.sorted_by_title(g.lists, utils.list_is_completed)
    return render_template(
        "lists.html", lists=lists, todos_remaining=utils.todos_remaining
    )


@app.route("/lists/new", methods=("GET", "POST"))
def create_list():
    if request.method == "POST":
        list_title = request.form["list_title"].strip()
        error = utils.error_for_list_title(list_title)

        if error is not None:
            flash(error, "error")
            return render_template("new_list.html")

        utils.add_list(list_title)
        flash("The list has been created.", "success")
        return redirect(url_for("get_lists"))

    return render_template("new_list.html")


@app.route("/lists/<list_id>")
def get_list(list_id):
    lst = {**utils.get_list(list_id)}
    lst["todos"] = utils.sorted_by_title(lst["todos"], lambda todo: todo["completed"])
    return render_template("list.html", lst=lst)


@app.route("/lists/<list_id>/todos", methods=("POST",))
def create_todo(list_id):
    lst = utils.get_list(list_id)

    todo_title = request.form["todo"].strip()
    error = utils.error_for_todo(todo_title)

    if error is not None:
        flash(error, "error")
        return render_template("list.html", lst=lst)

    utils.add_todo(list_id, todo_title)

    return redirect(url_for("get_list", list_id=list_id))


@app.route("/lists/<list_id>/todos/<todo_id>/status", methods=("POST",))
def update_todo_status(list_id, todo_id):
    new_val = request.form["completed"] == "True"
    utils.set_todo_completed(list_id, todo_id, new_val)
    flash("Todo status updated.", "success")

    return redirect(url_for("get_list", list_id=list_id))


@app.route("/lists/<list_id>/todos/<todo_id>/delete", methods=("POST",))
def delete_todo(list_id, todo_id):
    utils.delete_todo(list_id, todo_id)
    flash("Todo successfully deleted.", "success")

    return redirect(url_for("get_list", list_id=list_id))


@app.route("/lists/<list_id>/todos/complete-all", methods=("POST",))
def update_list_todos_status(list_id):
    utils.set_list_completed(list_id)
    flash("All todos marked as completed.", "success")

    return redirect(url_for("get_list", list_id=list_id))


@app.route("/lists/<list_id>/edit")
def edit_list(list_id):
    lst = utils.get_list(list_id)
    return render_template("edit_list.html", lst=lst)


@app.route("/lists/<list_id>", methods=("POST",))
def update_list(list_id):
    lst = utils.get_list(list_id)
    new_title = request.form["list_title"].strip()
    error = utils.error_for_list_title(new_title)

    if error is not None:
        flash(error, "error")
        return render_template("edit_list.html", lst=lst)

    utils.update_list_title(list_id, new_title)
    flash("List successfully updated.", "success")

    return redirect(url_for("get_list", list_id=list_id))


@app.route("/lists/<list_id>/delete", methods=("POST",))
def delete_list(list_id):
    utils.delete_list(list_id)
    flash("List successfully deleted.", "success")

    return redirect(url_for("get_lists"))


if __name__ == "__main__":
    app.run(debug=True, port=5003)
