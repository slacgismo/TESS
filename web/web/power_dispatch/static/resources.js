import React from "react";
import Chart from 'chart.js';

function normalizeToPercentage(ds) {
    if(!ds.length) {
        return ds;
    }
    // assume for now that the dataset is an array of ints
    const dsSum = ds.reduce((acc, item) => acc + item);
    const normalizer = 1 / dsSum;
    const normalizedDs = ds.map(item => (item * normalizer) * 100);
    return normalizedDs;
}

const datasets = {
    battery: [1,2,3],
    charger: [5,7,9],
    pv: [3,3,3],
    hvac: [10,15,3],
    hotWater: [12,1,9]
};

class ResourcesChart extends React.Component {
    componentDidMount() {
        // normalize the data set for each device to 1.0
        for (const property in datasets) {
            datasets[property] = normalizeToPercentage(datasets[property]);
        }

        // produce a totals array based on the previous vals and calc a normalized total
        let totalVals = []
        for (const property in datasets) {
            if(totalVals.length === 0) {
                totalVals = datasets[property];
            } else {
                totalVals = totalVals.map((val, idx) => {
                    return val + datasets[property][idx];
                });
            }
        }
        datasets["total"] = normalizeToPercentage(totalVals);

        // split the data across unavail/avail/dispatched
        const finalDataSet = {
            "unavailable": [],
            "available": [],
            "dispatched": []
        }

        for (const dsProp in datasets) {
            finalDataSet["unavailable"].push(datasets[dsProp][0]);
            finalDataSet["available"].push(datasets[dsProp][1]);
            finalDataSet["dispatched"].push(datasets[dsProp][2]);
        }

        this.updateChart(finalDataSet);
    }

    updateChart = (ds) => {
        const ctx = document.getElementById(this.props.id);
        new Chart(ctx, {
            // The type of chart we want to create
            type: 'bar',

            // The data for our dataset
            data: {
                labels: ['Total', 'Battery', 'Chargers', 'PV', 'HVAC', 'Hot Water'],
			    datasets: [
                    {
				        label: 'Dispatched',
				        backgroundColor: '#f5f590',
                        data: ds["dispatched"]
                    },
                    {
                        label: 'Available',
                        backgroundColor: '#426e2f',
                        data: ds["available"]
                    },
                    {
                        label: 'Unavailable',
                        backgroundColor: '#dbdbdb',
                        data: ds["unavailable"]
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
                        },
                        ticks: {
                            min: 0,
                            max: 100,
                            callback: function(value, index, values) {
                                return `${value}%`;
                            }
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

export default ResourcesChart;