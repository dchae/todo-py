from flask import session, g
from uuid import uuid4


def error_for_list_title(title):
    if len(title) not in range(1, 101):
        return "The title must be between 1 and 100 chars."

    if title in {lst["title"] for lst in g.lists.values()}:
        return "The title must be unique."


def error_for_todo(todo):
    if len(todo) not in range(1, 101):
        return "The Todo must be between 1 and 100 chars."


def get_list(list_id, lists):
    assert list_id in lists, "List could not be found"
    lst = lists[list_id]
    assert list_id == lst["id"], "List id does not match registered dict key"
    return lst


def add_list(list_title, lists):
    id = str(uuid4())
    new_list = {"id": id, "title": list_title, "todos": {}}
    lists[id] = new_list
    session.modified = True


def add_todo(todo_title, lst):
    todo_id = str(uuid4())
    todo = {"id": todo_id, "title": todo_title, "completed": False}
    lst["todos"][todo_id] = todo
    session.modified = True


def get_todo(todo_id, lst):
    assert todo_id in lst["todos"], "Todo could not be found"
    return lst["todos"][todo_id]


def set_todo_completed(todo, status):
    todo["completed"] = status
    session.modified = True


def set_list_completed(lst, status=True):
    todos = lst["todos"]
    for todo in todos.values():
        todo["completed"] = status
    session.modified = True


def delete_todo(lst, todo_id):
    todos = lst["todos"]
    assert todo_id in todos, "Todo could not be found"
    del todos[todo_id]
    session.modified = True
    # unneeded for del, but just for consistency


def update_list_title(lst, new_title):
    lst["title"] = new_title
    session.modified = True


def delete_list(list_id, lists):
    get_list(list_id, lists)
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
