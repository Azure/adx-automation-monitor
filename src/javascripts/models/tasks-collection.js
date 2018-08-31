export default class TasksCollection {
    constructor(tasks, failed, category) {
        this._tasks = tasks;
        this._failed = failed;
        this._category = category;

        this._orderBy = 'category';
        this._ascend = true;

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

    set sortBy(propertyName) {
        if (propertyName === this._orderBy) {
            this._ascend = !this._ascend;
        } else {
            this._orderBy = propertyName;
            this._ascend = true;
        }

        this._sort()
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

        this._sort()

        this._current_categories = new Set(this._current_collection.map(each => each.category));
    }

    _sort() {
        this._current_collection.sort((a, b) => {
            if (a[this._orderBy] < b[this._orderBy]) {
                return this._ascend ? -1 : 1
            } else if (a[this._orderBy] > b[this._orderBy]) {
                return this._ascend ? 1 : -1
            } else {
                return 0;
            }
        });
    }
}