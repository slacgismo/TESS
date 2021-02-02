import React from "react";
import Chart from 'chart.js';

class SystemLoadChart extends React.Component {

    updateChart = () => {
        const ctx = document.getElementById(this.props.id);
        // fixes child rendering before action dispatch for receiving data in parent
        if (ctx) {
            new Chart(ctx, {
                // The type of chart we want to create
                type: 'line',

                // The data for our dataset
                data: {
                    labels: this.props.ds ? this.props.ds.labels : [],
                    datasets: [
                        {
                            label: 'DS 01',
                            fill: false,
                            backgroundColor: 'rgb(255, 99, 132)',
                            borderColor: 'rgb(255, 99, 132)',
                            data: this.props.ds ? this.props.ds.one : []
                        },
                        {
                            label: 'DS 02',
                            fill: false,
                            backgroundColor: 'rgb(55, 99, 255)',
                            borderColor: 'rgb(55, 99, 255)',
                            data: this.props.ds ? this.props.ds.two : []
                        }
                    ]
                },

                // Configuration options go here
                options: {
                    responsive: true,
    				title: {
    					display: true,
    					text: this.props.chartTitle
                    },
                    legend: {
                        display: false
                    },
    				tooltips: {
    					mode: 'index',
    					intersect: false,
    				},
    				hover: {
    					mode: 'nearest',
    					intersect: true
    				},
    				scales: {
    					xAxes: [{
                            type: 'time',
                            time: {
                                unit: 'day'
                            },
    						display: true,
    						scaleLabel: {
    							display: true,
    							labelString: this.props.xTitle
    						}
    					}],
    					yAxes: [{
    						display: true,
    						scaleLabel: {
    							display: true,
    							labelString: this.props.yTitle
    						}
    					}]
    				}
                }
            });
        }
    }

    render() {
        this.updateChart();
        return (
            <canvas id={this.props.id} width="500" height="350"></canvas>
        );
    }
}

export default SystemLoadChart;
