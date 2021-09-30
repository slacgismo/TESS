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

class ResourcesChart extends React.Component {

    componentDidMount() {

        // normalize the data set for each device to 1.0
        for (const property in this.props.datasets) {
            this.props.datasets[property] = normalizeToPercentage(this.props.datasets[property]);
        }

        // produce a totals array based on the previous vals and calc a normalized total
        let totalVals = []
        for (const property in this.props.datasets) {
            if(totalVals.length === 0) {
                totalVals = this.props.datasets[property];
            } else {
                totalVals = totalVals.map((val, idx) => {
                    return val + this.props.datasets[property][idx];
                });
            }
        }

        this.props.datasets["total"] = normalizeToPercentage(totalVals);

        // TODO: will be usefull for v1.0
        // for (const dsProp in this.props.datasets) {
        //     if("unavailable" in this.props.finalDataSet) {
        //         this.props.finalDataSet["unavailable"].push(this.props.datasets[dsProp][0]);
        //     }
        //     if("available" in this.props.finalDataSet) {
        //         this.props.finalDataSet["available"].push(this.props.datasets[dsProp][1]);
        //     }
        //     if("dispatched" in this.props.finalDataSet) {
        //         this.props.finalDataSet["dispatched"].push(this.props.datasets[dsProp][2]);
        //     }
        // }
        if("unavailable" in this.props.finalDataSet) {
            this.props.finalDataSet["unavailable"].push(this.props.datasets['pv'][0]);
        }
        if("available" in this.props.finalDataSet) {
            this.props.finalDataSet["available"].push(this.props.datasets['pv'][1]);
        }
        if("dispatched" in this.props.finalDataSet) {
            this.props.finalDataSet["dispatched"].push(this.props.datasets['pv'][2]);
        }
        this.updateChart(this.props.finalDataSet);
    }


    updateChart = (ds) => {
        const ctx = document.getElementById(this.props.id);
        new Chart(ctx, {
            // The type of chart we want to create
            type: 'bar',

            // The data for our dataset
            data: {
                labels: ['PV'],
			    datasets: [
                    {
				        label: 'Dispatched',
				        backgroundColor: '#f5f590',
                        data: ds["dispatched"],
                        hidden: this.props.hiddenDataSets && this.props.hiddenDataSets["dispatched"]
                    },
                    {
                        label: 'Available',
                        backgroundColor: '#426e2f',
                        data: ds["available"],
                        hidden: this.props.hiddenDataSets && this.props.hiddenDataSets["available"]
                    },
                    {
                        label: 'Unavailable',
                        backgroundColor: '#dbdbdb',
                        data: ds["unavailable"],
                        hidden: this.props.hiddenDataSets && this.props.hiddenDataSets["unavailable"]
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
                    callbacks: {
                        label: function(tooltipItem, data) {
                            var label = data.datasets[tooltipItem.datasetIndex].label || '';

                            if (label) {
                                label += ': ';
                            }

                            label += Math.round(tooltipItem.yLabel * 100) / 100;
                            return label;
                        }
                    }
				},
				hover: {
					mode: 'nearest',
					intersect: true
                },
                legend: {
                    position: 'bottom'
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
