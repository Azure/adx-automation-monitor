import React from 'react';

export default class GeneralHeader extends React.Component {
    constructor(props) {
        super(props);
        this.data = pageData.entity.metadata;
    }

    getTitle() {
        return <h1 className="display-1">{this.data.type} <span className="display-4">{this.data.id}</span></h1>;
    }

    getMajorBadges() {
        return this.data.tags.major.map((tag, idx) =>
            <span className={this.getRepresentClassName(tag, "info")} key={idx}>{tag.value}</span>
        );
    }

    getMinorBadges() {
        return this.data.tags.minor.map((tag, idx) =>
            <span className={this.getRepresentClassName(tag, "secondary")} key={idx}>{tag.value}</span>
        );
    }

    getRepresentClassName(tag, defaultType) {
        let tagType = defaultType;
        if (tag.hasOwnProperty("type")) {
            tagType = tag.type;
        }

        return `badge badge-pill badge-${tagType} mr-1`;
    }

    render() {
        return <div className="jumbotron jumbotron-fluid">
            <div className="container">
                {this.getTitle()}
                <h3>
                    {this.getMajorBadges()}
                </h3>
                <h5>
                    {this.getMinorBadges()}
                </h5>
            </div>
        </div>
    }
}
