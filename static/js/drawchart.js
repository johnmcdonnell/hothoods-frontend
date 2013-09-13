
var chartmargin = {top: 20, right: 20, bottom: 90, left: 80},
    chartwidth = 400 - chartmargin.left - chartmargin.right,
    chartheight = 300 - chartmargin.top - chartmargin.bottom;
var parseDate = d3.time.format("%Y-%m-%d").parse;
var x = d3.time.scale()
    .range([0, chartwidth]);
var y = d3.scale.log()
    .base(2)
    .range([chartheight, 0]);
var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");
var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");
yAxis.tickFormat(d3.format("$d"));
var line = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.price); });
var errorspace = d3.svg.area()
    .x(function(d) { return x(d.date); })
    .y0(function(d) { return y(d.lo80); })
    .y1(function(d) { return y(d.hi80); });

var drawchart = function(zip) {
    $("#hoodinfo > svg").remove();
    d3.json("zip/"+zip, function(error, zipdata) {
        $("#hoodname").append(": " + zipdata.hoodname)
        $("#boroname").text(zipdata.boroname);
    var chartsvg = d3.select("#hoodinfo").append("svg")
        .attr("width", chartwidth + chartmargin.left + chartmargin.right)
        .attr("height", chartheight + chartmargin.top + chartmargin.bottom)
      .append("g")
        .attr("transform", "translate(" + chartmargin.left + "," + chartmargin.top + ")");
        //zipdata.SaleDate = zipdata.SaleDate.map(parseDate);
        zipdata.forecasts.forEach(function(d) {
            d.date = parseDate(d.date);
            d.price = +d.price;
        })
        zipdata.prices.forEach(function(d) {
            d.date = parseDate(d.date);
            d.price = +d.price;
        })
        x.domain(d3.extent(zipdata.prices.concat(zipdata.forecasts), function(d) { return d.date; }));
        y.domain([80,1600]); //d3.extent(zipdata.prices, function(d) { return d.ppsqft; }));
        
        // x-axis
        chartsvg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + chartheight + ")")
            .call(xAxis)
          .selectAll("text")
            .attr("y", 0)
            .attr("x", 9)
            .attr("dy", ".35em")
            .attr("transform", "rotate(90)")
            .style("text-anchor", "start");
        
        // y axis
        chartsvg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
          .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", -76)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Price / sq.ft.");
        
        // The line itself
        chartsvg.append("path")
            .datum(zipdata.prices)
            .attr("class", "line")
            .attr("d", line);
        // forecast
        chartsvg.append("path")
            .datum(zipdata.forecasts)
            .attr("class", "forecast")
            .attr("d", line);
        // Forecast error space
        chartsvg.append("path")
            .datum(zipdata.forecasts)
            .attr("class", "forecasterror")
            .attr("d", errorspace);
    });
}
