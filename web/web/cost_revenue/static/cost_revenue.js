import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import IntegralChart from './integral_chart';
import CashFlowChart from './cash_flow_chart';
import SurplusWelfareChart from './surplus_welfare_chart';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class CostRevenue extends React.Component {
    onClick = () => {}

    render() {
        return (
            <React.Fragment>
                <div className="chart-row-container">
                    <div className="chart-container">
                        <CashFlowChart xTitle="Time" yTitle="$/h" chartTitle="Cash Flow" />
                    </div>
                    <div className="chart-container">
                        <CashFlowChart xTitle="∫ Qdt" yTitle="$" chartTitle="Cash Flow" />
                    </div>
                </div>
                <div className="chart-row-container">
                    <div className="chart-container">
                        <SurplusWelfareChart xTitle="Time" yTitle="$/h" chartTitle="Surplus / Welfare"/>
                    </div>
                    <div className="chart-container">
                        <IntegralChart xTitle="Time" yTitle="$" chartTitle="Integral w.r.t Target" />
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