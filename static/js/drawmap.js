
// TODO: Encapsulate.
var viewpercent = d3.format("+.1p");
var uparrow = '<i class="ss-icon"></i>';
var downarrow = '<i class="ss-icon"></i>';

var trulia_allny = "http://www.trulia.com/for_sale/New_York,NY/x_map/";
var trulia_zip_template = _.template("http://www.trulia.com/for_sale/<%= zipcode %>_zip/x_map/");

var mapwidth=300;
var mapheight=500;
var mapsvg = d3.select("#map").append("svg")
    .attr("id", "map")
    .attr("width", mapwidth)
    .attr("height", mapheight);
var mapgroup = mapsvg.append('g');
var centered = null;

selected = [];

var growthbyzip = d3.map(),
    pricebyzip = d3.map(),
    hoodnamebyzip = d3.map(),
    mediangrowth;

var update_rec = function(zipname) {
    if (growthbyzip.get(zipname) > mediangrowth) {
        therm = uparrow;
        thermclass = "hot";
        word = "BUY";
        explain = "Prices rising faster than city median.";
    } else {
        therm = downarrow;
        thermclass = "cold";
        word = "Don't Buy";
        explain = "Prices rising slower than city median.";
    }
    $("#recword").text(word);
    $("#recexplain").text(explain);
    $("#recommendation").removeClass("hot cold").addClass(thermclass);
    $hoodinfo.find("#recthermo")
        .text("")
        .append(therm);
    }

var buildmap = function(error, nyc, mapinfo) {
    mapinfo.zips.forEach(function(d) {
        growthbyzip.set(d.zip, +d.growth);
        pricebyzip.set(d.zip, +d.price);
        hoodnamebyzip.set(d.zip, d.hoodname);
    });
    mediangrowth = d3.median(growthbyzip.values());
    var skippedhood = function(name) {
        // Return True if we don't have enough data to visualize.
        return growthbyzip.get(name) === undefined;
    };
    var clickhood = function(d, i) {
        var zipname = d.properties.zcta5ce00;
        if (skippedhood(zipname)) return;
        if (d && centered === null) {
            // Zoom into clicked item
            var centroid = path.centroid(d),
                x = centroid[0];
                y = centroid[1];
                k = 3;
            centered = d;
            d3.select(this).classed("maphover", false);
            $("#downarrow").fadeTo(0, 1);
            setup_trulia(zipname);
        } else {
            // Zoom out
            var x = mapwidth/2,
                y = mapheight/2,
                k = 1;
            centered = null;
            $("#downarrow").fadeTo(0, 0);
            $("#hoodinfo > svg").remove()
            d3.select(".maphover").classed("maphover", false);
            setup_trulia();
        }
        mapgroup.selectAll("path")
            .classed("activehood", centered && function(d) { return d === centered; });
        
        mapgroup.transition()
            .duration(750)
            .attr("transform", "translate(" + mapwidth/2 + "," + mapheight/2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
            .style("stroke-width", 1.5 / k + "px");
        drawchart(zipname);
    };
    var hover = function(d, i){
        zipname = d.properties.zcta5ce00;
        if (skippedhood(zipname)) return;
        if (centered === null) {
            d3.select(this).classed("maphover", true);
            $hoodinfo = $("#hoodinfo");
            $hoodinfo.find("svg").remove(); // TODO Shouldn't this just work when you 'unclick?
            $hoodinfo.fadeTo(0, 1);
            $("#hoodname").text(hoodnamebyzip.get(zipname));
            $("#zip").text(zipname);
            // $("#boroname").text(zipdata.boroname);
            $("#boroname").text("");
            update_rec(zipname);
        }
    };
    var unhover = function(d, i){
        if (centered === null) {
            d3.select(this).classed("maphover", false);
            $("#hoodinfo").fadeTo(0, 0);
        }
    };
    var quantizegrowth = d3.scale.quantize()
        .domain([-d3.max(growthbyzip.values())*.8, d3.max(growthbyzip.values())*.8])
        .range(d3.range(8).map(function(i) { return "q" + i + "-9"; }));
    
    var nyccenter = [-21450, 5300];
    var nycscale = 73000;
    var projection = d3.geo.albers()
        .translate(nyccenter)
        .scale(nycscale);
        // .center([0, 0])
    var path = d3.geo.path().projection(projection);
    mapgroup.selectAll('path')
        .data(nyc.features)
        .enter().append('path')
            .attr("class", function(d) { return quantizegrowth(growthbyzip.get(d.properties.zcta5ce00)); })
            .attr('d', path)
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
    $("#truliaframe").attr("src", url);
}

queue()
    .defer(d3.json, "static/geojson/nyc_zipcta.geojson")
    .defer(d3.json, "mapinfo.json")
    .await(buildmap)


