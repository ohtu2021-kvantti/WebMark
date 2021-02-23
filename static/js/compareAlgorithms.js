import {GoogleCharts} from 'google-charts';

GoogleCharts.load(drawChart, { packages: ['bar', 'corechart', 'line'] });

function drawChart() {
    const data = new google.visualization.DataTable();
    const a1Name = JSON.parse(document.getElementById('a1-name').textContent);
    const a2Name = JSON.parse(document.getElementById('a2-name').textContent);
    const graphData = JSON.parse(document.getElementById('graph-data').textContent);
    const algoData = JSON.parse(document.getElementById('algo-data').textContent);
    const columnData = GoogleCharts.api.visualization.arrayToDataTable(algoData);
    data.addColumn('number', 'X');
    data.addColumn('number', a1Name);
    data.addColumn('number', a2Name);
    data.addRows(graphData);

    const options = {
        width: 600,
        height: 480,
        title: "NOTE: Graphs are a work-in-progress and currently show dummy data",
        hAxis: {
            title: 'Iterations'
        },
        vAxis: {
            title: 'Accuracy'
        }
    };

    const chart = new GoogleCharts.api.visualization.LineChart(document.getElementById('chart_div'));
    const chart2 = new GoogleCharts.api.charts.Bar(document.getElementById('columnchart_material'));
    chart.draw(data, options);
    chart2.draw(columnData, GoogleCharts.api.charts.Bar.convertOptions(options));
}