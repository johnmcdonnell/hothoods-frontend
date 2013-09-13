
var viewpercent = d3.format("+.1p");
var uparrow = '<i style="color: black" class="icon-circle-arrow-up"></i>';
var downarrow = '<i style="color: black" class="icon-circle-arrow-down"></i>';

var trulia_allny = "http://www.trulia.com/for_sale/New_York,NY/x_map/";
var trulia_zip_template = _.template("http://www.trulia.com/for_sale/<%= zipcode %>_zip/x_map/");

var mapsvg = d3.select("#map").append("svg")
    .attr("id", "map")
    .attr("width", 400)
    .attr("height", 550);
var mapgroup = mapsvg.append('g');

selected = [];

var growthbyzip = d3.map();
var pricebyzip = d3.map();

var buildmap = function(error, nyc, mapinfo) {
    mapinfo.zips.forEach(function(d) {
        growthbyzip.set(d.zip, +d.growth);
        pricebyzip.set(d.zip, +d.price);
    });
    // console.log(mapinfo);
    var clickhood = function(d, i) {
        if (skippedhood(zipname)) return;
        zipname = d.properties.zcta5ce00;
        $("#hoodinfo").fadeTo(0, 1);
        $("#hoodname").text(zipname);
        $("#boroname").text("");
        drawchart(zipname);
        setup_trulia(zipname);
        
        // Box tracking selected neighborhoods. 
        // selectedbox = '<div class="selected"> <i style="color: green" class="icon-circle-arrow-up"></i>  <a onclick="(function(e) { e.preventdefault(); drawchart(<%= zip %>); })()"><%= zip %></a> <span style="float: right;"><i class="icon-search"></i> <i class="icon-remove"></i></span> </div>';
        // $("#selectedtray").append(_.template(selectedbox, {zip: zipname}));
    };
    var skippedhood = function(name) {
        // Return True if we don't have enough data to visualize.
        return growthbyzip.get(name) === undefined;
    };
    var hover = function(d, i){
        zipname = d.properties.zcta5ce00;
        if (skippedhood(zipname)) return;
        d3.select(this)
            .classed("mapselected", true);
        var growth =  growthbyzip.get(zipname);
        arrow = growth > 0 ? uparrow : downarrow;
        $("#tooltip h2").text("");
        $("#tooltip h2").append(arrow + " " + zipname );
        $("#tooltip-hoodheat").text(viewpercent(growth));
        $("#tooltip").show();
    };
    var unhover = function(d, i){
        d3.select(this)
            .classed("mapselected", false);
        //$("#hoodinfo").fadeTo(0, 0);
        $("#tooltip").hide();
    };
    var quantizegrowth = d3.scale.quantize()
        .domain([-d3.max(growthbyzip.values())*.8, d3.max(growthbyzip.values())*.8])
        .range(d3.range(8).map(function(i) { return "q" + i + "-9"; }));
    
    var projection = d3.geo.albers()
        .translate([-16300, 4100])
        .scale(56000);
        // .center([0, 0])
    mapgroup.selectAll('path')
        .data(nyc.features)
        .enter().append('path')
            .attr("class", function(d) { return quantizegrowth(growthbyzip.get(d.properties.zcta5ce00)); })
            .attr('d', d3.geo.path().projection(projection))
            //.attr('id', function(d){return d.properties.name.replace(/\s+/g, '')})
            // .style('fill', 'black')
            // .style('stroke', 'black')
            .on("mouseover", hover)
            .on("mouseout", unhover)
            .on("click", clickhood);
    setup_trulia();
};

var setup_trulia = function(zipcode) {
    var url = zipcode ? trulia_zip_template({zipcode: zipcode}) : trulia_allny;
    console.log(url);
    $("#truliaframe").attr("src", url);
}

queue()
    .defer(d3.json, "static/geojson/nyc_zipcta.geojson")
    .defer(d3.json, "mapinfo.json")
    .await(buildmap)


