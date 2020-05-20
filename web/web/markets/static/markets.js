import React from 'react';
import ReactDOM from 'react-dom';
import * as action from './actions';
import AuctionChart from './auction';
import { connect } from 'react-redux';
import { Switch } from '@rmwc/switch';
import { Button } from '@rmwc/button';
import HistoricalChart from './historical';
import { TextField } from '@rmwc/textfield';
import AuctionMarketChart from './auction_market';
import { selectMenuOption } from '../../static/js/actions';
import ConnectedComponentWrapper from '../../static/js/base';

import '@rmwc/switch/styles';
import '@rmwc/button/styles';
import '@rmwc/textfield/styles';

class Markets extends React.Component {
    componentDidMount() {
        // if a user decides to navigate back and forth through the
        // browser arrows, the menu selection won't update accordingly,
        // so we fix that by having each component do it, 😔, this is 
        // not great since the component shouldn't care about the menu
        this.props.dispatch(selectMenuOption('markets'));        
    }

    render() {
        return (
            <div className="power-dispatch-container">
                <div className="power-dispatch-margin-fix">
                    <div className="power-dispatch-chart-container">
                        <div className="pd-chart-system-load">
                            <AuctionMarketChart
                                id="auction-market-chart"
                                xTitle="Capacity (MW)" 
                                yTitle="Price ($/MWh)"
                                chartTitle="Auction Market"
                                chartSubtitle="Transformer Capacity" />
                        </div>
                        <div className="pd-chart-resource">
                            <AuctionChart
                                id="auction-chart"
                                xTitle="Time" 
                                yTitle="Price ($/MWh)"
                                chartTitle="Auction"
                                chartSubtitle="" />
                        </div>
                    </div>

                    <div className="power-dispatch-forms-container">
                        <div className="pd-form-container">
                            <div className="pd-form-title">
                                <h3>Constraint and Alert Settings</h3>
                            </div>

                            <div>
                                <h4>Alarms</h4>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Yellow Alarm</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">%</div>
                                </div>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Red Alarm</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">%</div>
                                </div>
                            </div>
                            
                            <hr />
                            
                            <div>
                                <h4>Alerts</h4>
                                <div className="pd-form-row">
                                    <div className="pd-form-element-label">Price</div>
                                    <div className="pd-form-element-input">
                                        <TextField outlined />
                                    </div>
                                    <div className="pd-form-element-unit">Percentile</div>
                                </div>
                            </div>
                            
                            <hr />
                            
                            <div className="pd-form-button-container">
                                <Button 
                                    label="SET" 
                                    onClick={this.addNewRow}
                                    outlined />
                            </div>
                        </div>    
                    
                        <div className="pd-form-container">
                            <div className="pd-chart-system-load">
                                <HistoricalChart
                                    id="historical-market-chart"
                                    xTitle="Time" 
                                    yTitle="Price ($/MWh)"
                                    chartTitle="Historical Data" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

const ConnectedMarkets = connect(state => ({}))(Markets);

const marketsElement = (
    <ConnectedComponentWrapper isVisible={true} pageTitle="MARKETS">
        <ConnectedMarkets/>
    </ConnectedComponentWrapper>
);
ReactDOM.render(marketsElement, document.getElementById('master-container'));