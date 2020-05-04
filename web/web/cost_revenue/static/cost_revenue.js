import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import CostRevenueChart from './cost_revenue_charts';
import ConnectedComponentWrapper from '../../static/js/base';

import * as action from './actions';

class CostRevenue extends React.Component {
    render() {
        return (
            <div className="cost-revenue-main-content-container">
                <div className="chart-row-container">
                    <div className="chart-container">                        
                        <CostRevenueChart 
                            xTitle="Time" 
                            yTitle="$/h" 
                            chartTitle="Cash Flow"
                            chartSubtitle="" />
                    </div>
                    <div className="chart-container chart-divider"></div>
                    <div className="chart-container">
                        <CostRevenueChart 
                            xTitle="Time" 
                            yTitle="$/h" 
                            chartTitle="Surplus / Welfare"
                            chartSubtitle="" />
                    </div>
                </div>
                <br />
                <div className="chart-row-container">
                    <div className="chart-container">
                        <CostRevenueChart 
                            xTitle="∫ Qdt" 
                            yTitle="$"
                            chartTitle="Cash Flow"
                            chartSubtitle="" />                        
                    </div>
                    <div className="chart-container chart-divider"></div>
                    <div className="chart-container">
                        <CostRevenueChart 
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

const ConnectedCostRevenue = connect(state => ({}))(CostRevenue);

const costRevenueElement = (
    <ConnectedComponentWrapper isVisible={true}>
        <ConnectedCostRevenue/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(costRevenueElement, document.getElementById('master-container'));