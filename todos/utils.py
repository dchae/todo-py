from flask import abort, session, g
from uuid import uuid4


def error_for_list_title(title):
    if len(title) not in range(1, 101):
        return "The title must be between 1 and 100 chars."

    if title in {lst["title"] for lst in g.lists.values()}:
        return "The title must be unique."


def error_for_todo(todo):
    if len(todo) not in range(1, 101):
        return "The Todo must be between 1 and 100 chars."


def get_list(list_id):
    if list_id not in g.lists:
        abort(404, "List could not be found")

    lst = g.lists[list_id]
    assert list_id == lst["id"], "List id does not match registered dict key"
    return lst


def get_todos(list_id):
    lst = get_list(list_id)
    return lst["todos"]


def add_list(list_title):
    id = str(uuid4())
    new_list = {"id": id, "title": list_title, "todos": {}}
    g.lists[id] = new_list
    session.modified = True


def add_todo(list_id, todo_title):
    todo_id = str(uuid4())
    todo = {"id": todo_id, "title": todo_title, "completed": False}
    lst = g.lists[list_id]
    lst["todos"][todo_id] = todo
    session.modified = True


def get_todo(list_id, todo_id):
    lst = get_list(list_id)
    if todo_id not in lst["todos"]:
        abort(404, "Todo could not be found")
    return lst["todos"][todo_id]


def set_todo_completed(list_id, todo_id, status):
    todo = get_todo(list_id, todo_id)
    todo["completed"] = status
    session.modified = True


def set_list_completed(list_id, status=True):
    todos = get_todos(list_id)
    for todo in todos.values():
        todo["completed"] = status
    session.modified = True


def delete_todo(list_id, todo_id):
    todos = get_todos(list_id)
    if todo_id not in todos:
        abort(404, "Todo could not be found")
    del todos[todo_id]
    session.modified = True
    # unneeded for del, but just for consistency


def update_list_title(list_id, new_title):
    lst = get_list(list_id)
    lst["title"] = new_title
    session.modified = True


def delete_list(list_id):
    get_list(list_id)
    del g.lists[list_id]
    session.modified = True


def todos_remaining(lst):
    return len([todo for todo in lst["todos"].values() if not todo["completed"]])


def list_is_completed(lst):
    return todos_remaining(lst) == 0


def sorted_by_title(nested_dict, condition=lambda x: True):
    not_completed, completed = [], []
    for val in sorted(nested_dict.values(), key=lambda val: val["title"].casefold()):
        (not_completed, completed)[condition(val)].append(val)

    return {**{v["id"]: v for v in not_completed}, **{v["id"]: v for v in completed}}
