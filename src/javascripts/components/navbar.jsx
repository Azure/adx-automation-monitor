import React from "react";

export default class Navbar extends React.Component {
    constructor(props) {
        super(props);
        this.links = pageData.links;
        this.user = pageData.user;
    }

    render() {
        let navLinks = <ul className="navbar-nav mr-auto">
            {this.links.map(each =>
                <li key={each.name} className="nav-item">
                    <a className="nav-link" href={each.link}>{each.name}</a>
                </li>
            )}
        </ul>;

        let navUser = "";
        if (this.user.is_authenticated) {
            navUser = <ul className="navbar-nav">
                <li className="nav-item">
                    <a className="nav-link" href="#">{this.user.name}</a>
                </li>
            </ul>
        }

        return <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
            <a className="navbar-brand" href="#">A01 Automation</a>
            <div className="collapse navbar-collapse">
                {navLinks}
                {navUser}
            </div>
        </nav>
    }
}
