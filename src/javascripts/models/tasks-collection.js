export default class TasksCollection {
    constructor(tasks, failed, category) {
        this._tasks = tasks.sort(TasksCollection.categorySorter);
        this._failed = failed;
        this._category = category;
        this._filter();
    }

    set failed(state) {
        if (state !== this._failed) {
            this._failed = state;
            this._filter();
        }
    }

    set category(state) {
        if (state !== this._category) {
            this._category = state;
            this._filter();
        }
    }

    get tasks() {
        return this._current_collection;
    }

    get categories() {
        return this._current_categories;
    }

    _filter() {
        this._current_collection = this._tasks
            .filter(each => {
                if (this._failed) {
                    return each.result !== "Passed";
                } else {
                    return true;
                }
            })
            .filter(each => {
                return this._category === undefined || this._category === "" || each.category === this._category;
            });

        this._current_categories = new Set(this._current_collection.map(each => each.category));
    }

    static categorySorter(lhs, rhs) {
        if (lhs.category < rhs.category) {
            return -1;
        } else if (lhs.category > rhs.category) {
            return 1;
        } else {
            return 0;
        }
    }
}