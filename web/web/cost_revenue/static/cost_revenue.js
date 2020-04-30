import React from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';
import ConnectedComponentWrapper from '../../static/base';

import { Chart } from "react-google-charts";

import * as action from './actions';

class CostRevenue extends React.Component {
    onClick = () => {
        this.props.dispatch(action.loginSuccessful('asdf'));
    }

    render() {
        return (
            <div className="">
                <Chart
                chartType="ScatterChart"
                data={[["Age", "Weight"], [4, 5.5], [8, 12]]}
                width="100%"
                height="400px"
                legendToggle
                />
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