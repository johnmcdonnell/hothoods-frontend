
selected = [];


var buildmap = function(error, nyc) {
    console.log('hi there!!');
    var clickhood = function(d, i) {
        zipname = d.properties.zcta5ce00;
        $("#hoodinfo").fadeTo(0, 1);
        $("#hoodname").text(zipname);
        $("#boroname").text("");
        drawchart(zipname);
        
        selected = '<div class="selected"> <i style="color: green" class="icon-circle-arrow-up"></i>  <a onclick="(function(e) { e.preventdefault(); drawchart(<%= zip %>); })()"><%= zip %></a> <span style="float: right;"><i class="icon-search"></i> <i class="icon-remove"></i></span> </div>';
        $("#selectedtray").append(_.template(selected, {zip: zipname}));
    };
    var skippedhood = function(name) {
        // Return True if we don't have enough data to make this 
        // Not yet implemented.
        return false;
    };
    var hover = function(d, i){
        zipname = d.properties.zcta5ce00;
        if (skippedhood(zipname)) return;
        d3.select(this)
            .style("fill", "gray")
            .style('stroke', 'gray');
    };
    var unhover = function(d, i){
        d3.select(this)
            .style("fill", "black")
            .style('stroke', 'black');
        //$("#hoodinfo").fadeTo(0, 0);
    };
    var quantize = d3.scale.quantize()
        .domain([0, .15])
        .range(d3.range(9).map(function(i) { return "q" + i + "-9"; }));
    
    var projection = d3.geo.albers()
        .translate([-16300, 4100])
        .scale(56000);
        // .center([0, 0])
    group.selectAll('path')
    .data(nyc.features)
    .enter().append('path')
        .attr('d', d3.geo.path().projection(projection))
        //.attr('id', function(d){return d.properties.name.replace(/\s+/g, '')})
        .style('fill', 'black')
        .style('stroke', 'black')
        .on("mouseover", hover)
        .on("mouseout", unhover)
        .on("click", clickhood);
};

queue()
    .defer(d3.json, "static/geojson/nyc_zipcta.geojson", buildmap)
    .defer(d3.json, "mapinfo.json")
    .await(buildmap, function(x, y, z) {console.log("await concluded");});

