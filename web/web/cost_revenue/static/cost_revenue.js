import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import CashFlowChart from './cash_flow_chart';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class CostRevenue extends React.Component {
    onClick = () => {}

    render() {
        return (
            <React.Fragment>
                <div className="chart-row-container">
                    <div className="chart-container">
                        <CashFlowChart xTitle="Time" yTitle="$/h"/>
                    </div>
                    <div className="chart-container">
                        <CashFlowChart xTitle="∫ Qdt" yTitle="$" />
                    </div>
                </div>
            </React.Fragment>
        );
    }
}

const ConnectedCostRevenue = connect(state => ({}))(CostRevenue);

const costRevenueElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedCostRevenue/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(costRevenueElement, document.getElementById('master-container'));