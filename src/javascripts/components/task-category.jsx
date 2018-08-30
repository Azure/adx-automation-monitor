function TaskCategoryBadge(props) {
    let className = "badge badge-pill mr-1";
    if (props.selected) {
        className += " badge-dark"
    } else {
        className += " badge-secondary"
    }

    return <span className={className} onClick={() => props.onClick()}>{props.name}</span>
}

function TaskCategoriesBadges(props) {
    return Array.from(props.categories).map(
        each => <TaskCategoryBadge name={each}
                                   selected={each == props.current_category}
                                   onClick={() => props.onClick(each)} />
    )
}

function TaskCategoryResetBadge(props) {
    return <span className="badge badge-pill badge-success mr-1" onClick={() => props.onClick()}>reset</span>
}

export { TaskCategoryBadge, TaskCategoryResetBadge, TaskCategoriesBadges };