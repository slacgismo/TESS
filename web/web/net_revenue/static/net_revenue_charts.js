import React from "react";
import Chart from 'chart.js';

class CostRevenueChart extends React.Component {
    componentDidMount() {
        this.updateChart();
    }

    updateChart = () => {
        const ctx = document.getElementById(this.props.id);
        new Chart(ctx, {
            // The type of chart we want to create
            type: 'line',

            // The data for our dataset
            data: {
                labels: this.props.ds ? this.props.ds.labels : [],
                datasets: [
                    {
                        label: 'My First dataset',
                        fill: false,
                        backgroundColor: 'rgb(255, 99, 132)',
                        borderColor: 'rgb(255, 99, 132)',
                        data: this.props.ds ? this.props.ds.one : []
                    },
                    {
                        label: 'My Second dataset',
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

    render() {
        return (
            <canvas id={this.props.id} width="500" height="400"></canvas>
        );
    }
}

export default CostRevenueChart;
