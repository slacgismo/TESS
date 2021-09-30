import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import CostRevenueChart from './net_revenue_charts';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class CostRevenue extends React.Component {
    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('net-revenue'));
        this.props.dispatch(action.getCashFlowData());
    }

    render() {
        return (
            <div className="net-revenue-main-content-container">
                <div className="chart-row-container">
                    <div className="chart-container">
                        <CostRevenueChart
                            id="cr-chart-cash-flow"
                            xTitle="Time"
                            yTitle="$/h"
                            chartTitle="Cash Flow"
                            chartSubtitle=""
                            ds={this.props.cashFlowData.cashFlow} />
                    </div>
                    <div className="chart-container chart-divider"></div>
                    <div className="chart-container">
                        <CostRevenueChart
                            id="cr-chart-cash-flow-integral"
                            xTitle="∫ Qdt"
                            yTitle="$"
                            chartTitle="Cash Flow (Integral)"
                            chartSubtitle=""
                            ds={this.props.cashFlowData.cashFlowIntegral} />
                    </div>
                </div>
                <br />
                <div className="chart-row-container">
                    <div className="chart-container">
                        <CostRevenueChart
                            id="cr-chart-surplus-welfare"
                            xTitle="Time"
                            yTitle="$/h"
                            chartTitle="Surplus / Welfare"
                            chartSubtitle="" />
                    </div>
                    <div className="chart-container chart-divider"></div>
                    <div className="chart-container">
                        <CostRevenueChart
                            id="cr-chart-integral-target"
                            xTitle="Time"
                            yTitle="$"
                            chartTitle="Integral W.R.T. Target"
                            chartSubtitle="" />
                    </div>
                </div>
            </div>
        );
    }
}

const ConnectedCostRevenue = connect(state => ({
    cashFlowData: state.netRevenue.cashFlowData,
}))(CostRevenue);

const costRevenueElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="NET REVENUE">
        <ConnectedCostRevenue/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(costRevenueElement, document.getElementById('master-container'));
