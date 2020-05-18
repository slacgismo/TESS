import React from "react";
import { Chart } from "react-google-charts";

const SystemLoadChart = props => {
    return (
        <Chart
            width={'500px'}
            height={'400px'}
            chartType="Line"
            loader={<div>Loading Chart</div>}
            data={[
                [
                    { type: props.type, label: props.xTitle }, 
                    'Label One', 
                    'Label Two'
                ],
                [0, 0, 0],
                [1, 10, 5],
                [2, 23, 15],
                [3, 17, 9],
                [4, 18, 10],
                [5, 9, 5],
                [6, 11, 3],
                [7, 27, 19]
            ]}
            options={{
                chart: {
                    title: props.chartTitle,
                    subtitle: props.chartSubtitle
                },
                series: {
                    0: { axis: "yTitle" }, 
                    1: { axis: "yTitle" }
                },
                axes: {                    
                    y: {
                        yTitle: { label: props.yTitle }
                    }
                }
            }}
        />
    );
}

export default SystemLoadChart;