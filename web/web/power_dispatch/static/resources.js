import React from "react";
import { Chart } from "react-google-charts";

const ResourcesChart = props => {
    return (
        <Chart
            width={'500px'}
            height={'300px'}
            chartType="Bar"
            loader={<div>Loading Chart</div>}
            data={[
                ['', 'Unvailable', 'Available', 'Dispatched'],
                ['Total', 1000, 400, 200],
                ['Batteries', 1170, 460, 250],
                ['Chargers', 1660, 120, 300],
                ['PV', 1030, 540, 350],
                ['HVAC', 1030, 540, 350],
                ['Hot Water', 1030, 540, 350],
            ]}
            options={{
                // Material design options
                chart: {
                    title: props.chartTitle,
                    subtitle: '',
                },
                isStacked: 'percent',
                bars: 'horizontal'
            }}
            // For tests
            rootProps={{ 'data-testid': '2' }}
        />
    )
};

export default ResourcesChart;