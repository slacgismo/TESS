import React from "react";
import Chart from 'chart.js';

class AuctionMarketChart extends React.Component {
    componentDidMount() {
        this.updateChart();
    }

    updateChart = () => {
        const ctx = document.getElementById(this.props.id);
        new Chart(ctx, {
            // The type of chart we want to create
            type: 'bar',

            // The data for our dataset
            data: {
                labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
			    datasets: [
                    {
                        label: 'Dataset 1',
                        backgroundColor: 'red',
                        data: []
                    },
                    {
                        label: 'Dataset 2',
                        backgroundColor: 'blue',
                        data: []
                    },
                    {
				        label: 'Dataset 3',
				        backgroundColor: 'green',
                        data: []
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
                        stacked: true,
						display: true,
						scaleLabel: {
							display: true,
							labelString: this.props.xTitle
						}
					}],
					yAxes: [{
                        stacked: true,
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

    render() {
        return (
            <canvas id={this.props.id} width="500px" height="350px"></canvas>
        );
    }
}

export default AuctionMarketChart;
