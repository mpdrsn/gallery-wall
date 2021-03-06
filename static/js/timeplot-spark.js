
function plotAllTimeData(data) {

    var nPlots = data['all_plots'].length;

    for(var i=0; i<nPlots; i++){

        var canvasColumnHtml = "<div class='col-xs-12 col-sm-6 col-md-4 col-lg-4'>";
        var canvasHtml = "<canvas id=\"plot" + i + "\" width=\"300\" height=\"130\"></canvas>";

        var title = data['all_labels'][i];
        var titleHtml = '<h6>' + title + '</h6>';

        var plotHtml = (
                        canvasColumnHtml + titleHtml + canvasHtml + '</div>'
                        );

        var typeId = '#' + data['all_types'][i];
        $(typeId).append(plotHtml);

        var options = {
                       // legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>",
                       scaleOverride: true,
                       scaleSteps: 5,
                       scaleStepWidth: 0.2,
                       scaleStartValue: 0,
                       scaleShowLabels: false};

        var ctx = document.getElementById(("plot"+i)).getContext("2d");
        var myBarChart = new Chart(ctx).Bar(data['all_plots'][i], options);
        $(("#legend-plot" + i)).html(myBarChart.generateLegend());
    }

}

$.get('gettime.json', plotAllTimeData);
