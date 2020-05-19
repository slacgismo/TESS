import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ResourcesChart from './resources';
import SystemLoadChart from './system_load';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class Capacity extends React.Component {
    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is 
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('power-dispatch'));
    }

    render() {
        return (
            <div className="power-dispatch-container">
                <div className="power-dispatch-margin-fix">
                    <div className="power-dispatch-chart-container">
                        <div className="pd-chart-system-load">
                            <SystemLoadChart 
                                xTitle="Hours" 
                                yTitle="MW" 
                                chartTitle="System Load"
                                chartSubtitle="Transformer Capacity" />
                        </div>
                        <div className="pd-chart-resource">
                            <ResourcesChart 
                                xTitle="Hours" 
                                yTitle="MW" 
                                chartTitle="Resources in the System"
                                chartSubtitle="" />
                        </div>
                    </div>
                    <div className="power-dispatch-form-container">
                        <p>a random form</p>
                    </div>
                </div>
            </div>
        );
    }
}

const ConnectedCapacity = connect(state => ({}))(Capacity);

const capacityElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="CAPACITY">
        <ConnectedCapacity/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(capacityElement, document.getElementById('master-container'));