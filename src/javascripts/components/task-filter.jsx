export default function TaskFilterBadge(props) {
    let className = "badge badge-pill mr-1";
    if (props.failed) {
        className += " badge-danger";
    } else {
        className += " badge-success";
    }

    return <span className={className} onClick={() => props.onClick()}>{props.failed ? "failed" : "all"}</span>
}
