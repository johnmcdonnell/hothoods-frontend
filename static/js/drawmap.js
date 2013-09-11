
var mapsvg = d3.select("#main").insert("svg", "#hoodinfo")
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
    };
    var unhover = function(d, i){
        d3.select(this)
            .classed("mapselected", false);
        //$("#hoodinfo").fadeTo(0, 0);
    };
    var quantizegrowth = d3.scale.quantize()
        // HACK! 
        .domain([d3.min(growthbyzip.values())/3, d3.max(growthbyzip.values())/2])
        .range(d3.range(9).map(function(i) { return "q" + i + "-9"; }));
    
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
};

queue()
    .defer(d3.json, "static/geojson/nyc_zipcta.geojson")
    .defer(d3.json, "mapinfo.json")
    .await(buildmap)


