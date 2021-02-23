import {GoogleCharts} from 'google-charts';

GoogleCharts.load(drawChart, { packages: ['bar', 'corechart', 'line'] });

function drawChart() {
    var data = new google.visualization.DataTable();
    var a1Name = JSON.parse(document.getElementById('a1-name').textContent);
    var a2Name = JSON.parse(document.getElementById('a2-name').textContent);
    var graphData = JSON.parse(document.getElementById('graph-data').textContent);
    var algoData = JSON.parse(document.getElementById('algo-data').textContent);
    var columnData = GoogleCharts.api.visualization.arrayToDataTable(algoData);
    data.addColumn('number', 'X');
    data.addColumn('number', a1Name);
    data.addColumn('number', a2Name);
    data.addRows(graphData);

    var options = {
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

    var chart = new GoogleCharts.api.visualization.LineChart(document.getElementById('chart_div'));
    var chart2 = new GoogleCharts.api.charts.Bar(document.getElementById('columnchart_material'));
    chart.draw(data, options);
    chart2.draw(columnData, GoogleCharts.api.charts.Bar.convertOptions(options));
}